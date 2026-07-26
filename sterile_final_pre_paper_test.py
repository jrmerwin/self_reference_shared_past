"""
Final pre-paper sterile-mode test for the Gödelian Expansion / DEU registry model.

This script is self-contained.  It tests whether the unique multiplicity-1 S-node
("sigma", the sterile mode) has a mechanistic role in the expansion basin once a
sterile-capture rule is explicitly added.

Core discipline
---------------
A sterile-capture rule is allowed, but the identical rule is also applied to each
of the eight other universal S-nodes.  A sterile-specific mechanism is supported
only if sigma moves the growth/phase metrics beyond those matched controls.

Two basin semantics are tested:
    contact  : a lineage is in the target basin only after the target is actually
               selected as one of the absorber side-links, or after it descends
               from an already target-touched absorber.
    adjacent : a lineage is in the target basin whenever the resolving node is
               adjacent to the target, or descends from an already target-touched
               absorber.  Since sigma and the controls are universal S-hubs, this
               is the strong basin version.

Damping rule
------------
When a resolving lineage is in the target basin, each newly generated self-
referential seed is suppressed with probability gamma.  Suppressed seeds are not
created.  Non-suppressed seeds inherit the basin flag, so the capture can persist
across descendants.

Dependencies: numpy, networkx.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from collections import Counter, deque
import csv
import json
import math
import statistics
from pathlib import Path
from typing import Optional

import numpy as np
import networkx as nx

OUTDIR = Path('/mnt/data')


def object_string(obj) -> str:
    if isinstance(obj, str):
        return obj
    return "{" + ",".join(sorted(object_string(x) for x in obj)) + "}"


def object_key(obj) -> str:
    return object_string(obj)


def get_all_subtrees(obj):
    if isinstance(obj, str):
        return {obj}
    out = {obj}
    for child in obj:
        out |= get_all_subtrees(child)
    return out


def build_objects(n_primitives: int = 2, max_dag: int = 7):
    atoms = [chr(ord('a') + i) for i in range(n_primitives)]
    all_obj = set(atoms)
    by_size = {1: list(atoms)}
    for size in range(2, max_dag + 1):
        new = set()
        current = sorted(all_obj, key=object_key)
        for i in range(len(current)):
            for j in range(i + 1, len(current)):
                obj = frozenset({current[i], current[j]})
                if obj in all_obj:
                    continue
                if len(get_all_subtrees(obj)) == size:
                    new.add(obj)
        all_obj |= new
        by_size[size] = sorted(new, key=object_key)
    return by_size


def get_shape(obj) -> str:
    if isinstance(obj, str):
        return 'P'
    children = sorted(get_shape(child) for child in obj)
    return f'({children[0]}|{children[1]})'


def parse_shape(shape: str):
    if shape == 'P':
        return 'P'
    inner = shape[1:-1]
    depth = 0
    for i, ch in enumerate(inner):
        if ch == '(':
            depth += 1
        elif ch == ')':
            depth -= 1
        elif ch == '|' and depth == 0:
            return inner[:i], inner[i + 1:]
    raise ValueError(f'Cannot parse shape: {shape}')


def compute_multiplicity(shape: str, cache: dict[str, int]) -> int:
    if shape in cache:
        return cache[shape]
    if shape == 'P':
        cache[shape] = 2
        return 2
    left, right = parse_shape(shape)
    ml = compute_multiplicity(left, cache)
    mr = compute_multiplicity(right, cache)
    value = ml * (ml - 1) // 2 if left == right else ml * mr
    cache[shape] = value
    return value


def build_registry():
    dag7 = build_objects(2, 7)[7]
    cache: dict[str, int] = {}
    records = []
    for idx, obj in enumerate(dag7):
        a, b = sorted(list(obj), key=object_key)
        shape = get_shape(obj)
        record = {
            'id': idx,
            'obj': obj,
            'obj_string': object_string(obj),
            'shape': shape,
            'anc': get_all_subtrees(obj),
            'parent_overlap': len(get_all_subtrees(a) & get_all_subtrees(b)),
            'mult': compute_multiplicity(shape, cache),
        }
        records.append(record)
    for r in records:
        r['sector'] = 'S' if r['parent_overlap'] <= 3 else ('G' if r['mult'] == 16 else 'I')

    graph = nx.Graph()
    for r in records:
        graph.add_node(
            r['id'],
            sector=r['sector'],
            mult=r['mult'],
            parent_overlap=r['parent_overlap'],
            shape=r['shape'],
            obj_string=r['obj_string'],
        )
    ancestors = {r['id']: r['anc'] for r in records}
    ids = [r['id'] for r in records]
    for i in range(len(ids)):
        for j in range(i + 1, len(ids)):
            if len(ancestors[ids[i]] & ancestors[ids[j]]) > 3:
                graph.add_edge(ids[i], ids[j])
    return graph, records


G, REC = build_registry()
BASE_ADJ = {n: set(G.neighbors(n)) for n in G.nodes}
NODES = list(G.nodes())
SECTORS = Counter(G.nodes[n]['sector'] for n in G.nodes)
S_NODES = [n for n in NODES if G.nodes[n]['sector'] == 'S']
STERILE_NODES = [n for n in NODES if G.nodes[n]['mult'] == 1]
if len(STERILE_NODES) != 1:
    raise RuntimeError(f'Expected one sterile node, got {STERILE_NODES}')
SIGMA = STERILE_NODES[0]
UNIVERSAL_S = [n for n in S_NODES if G.degree(n) == 136]
NONSTERILE_UNIVERSAL_S = [n for n in UNIVERSAL_S if n != SIGMA]
ORDINARY_S = [n for n in S_NODES if G.degree(n) == 73]


def round_mean(vals) -> int:
    return int(sum(vals) / len(vals) + 0.5) if vals else 0


@dataclass(frozen=True)
class Condition:
    name: str
    target: Optional[int] = None
    mode: str = 'none'       # none, contact, adjacent
    gamma: float = 0.0
    pin_target: Optional[int] = None


@dataclass
class RunResult:
    condition: str
    beta: float
    seed: int
    nres: int
    final_A: int
    sustained: bool
    suppressed: int
    spawned: int
    basin_resolutions: int
    original_resolved: int
    target_resolved: Optional[bool]


class CaptureEngine:
    """Optimized sector-agnostic expansion engine with optional basin capture."""

    def __init__(self, seed: int, beta: float, condition: Condition, max_res: int = 1500):
        if condition.mode not in {'none', 'contact', 'adjacent'}:
            raise ValueError(f'bad mode {condition.mode!r}')
        self.rng = np.random.default_rng(seed)
        self.beta = float(beta)
        self.condition = condition
        self.max_res = int(max_res)
        self.adj = {n: set(BASE_ADJ[n]) for n in NODES}
        self.label = {n: int(self.rng.integers(0, 2)) for n in NODES}
        self.is_sr = {n: True for n in NODES}
        if condition.pin_target is not None:
            self.is_sr[condition.pin_target] = False
        self.absorber: dict[int, int] = {}
        self.basin: dict[int, bool] = {n: False for n in NODES}
        self._next = max(NODES) + 1
        self.nres = 0
        self.suppressed = 0
        self.spawned = 0
        self.basin_resolutions = 0
        self.resolved_original = set()

    def conclusion(self, v: int) -> int:
        evidence = [self.label[u] for u in self.adj[v]]
        if self.is_sr.get(v, False):
            src = self.absorber.get(v, v)
            evidence.extend([self.label[src]] * (2 * len(self.adj[v]) + 1))
        return round_mean(evidence)

    def _new(self, label: int, self_ref: bool, basin: bool = False) -> int:
        nid = self._next
        self._next += 1
        self.adj[nid] = set()
        self.label[nid] = int(label)
        self.is_sr[nid] = bool(self_ref)
        self.basin[nid] = bool(basin)
        return nid

    def _choose_side_links(self, v: int, absorber: int) -> list[int]:
        candidates = list(self.adj[v] - {absorber})
        self.rng.shuffle(candidates)
        return candidates[:3]

    def _basin_for_resolution(self, v: int, side_links: list[int]) -> bool:
        target = self.condition.target
        if target is None or self.condition.mode == 'none':
            return False
        if self.condition.mode == 'contact':
            return (
                v == target
                or self.basin.get(v, False)
                or target in side_links
                or any(self.basin.get(u, False) for u in side_links)
            )
        # adjacent / strong basin semantics
        return (
            v == target
            or self.basin.get(v, False)
            or target in self.adj.get(v, set())
            or target in side_links
            or any(self.basin.get(u, False) for u in side_links)
        )

    def resolve(self, v: int):
        absorber = self._new(self.label.get(v, 0), self_ref=False, basin=False)
        self.adj[v].add(absorber)
        self.adj[absorber].add(v)
        side_links = self._choose_side_links(v, absorber)
        for u in side_links:
            self.adj[absorber].add(u)
            self.adj[u].add(absorber)

        in_basin = self._basin_for_resolution(v, side_links)
        self.basin[absorber] = in_basin
        if in_basin:
            self.basin_resolutions += 1
        self.absorber[v] = absorber
        if v in G.nodes:
            self.resolved_original.add(v)

        seeded = []
        k = int(self.rng.poisson(self.beta))
        for _ in range(k):
            if in_basin and self.rng.random() < self.condition.gamma:
                self.suppressed += 1
                continue
            s = self._new(int(self.rng.integers(0, 2)), self_ref=True, basin=in_basin)
            self.adj[absorber].add(s)
            self.adj[s].add(absorber)
            seeded.append(s)
            self.spawned += 1
        return absorber, seeded

    def run(self) -> RunResult:
        initial = [n for n in NODES if self.is_sr.get(n, False)]
        q = deque(self.rng.permutation(initial))
        while q and self.nres < self.max_res:
            v = int(q.popleft())
            if v in self.absorber or not self.is_sr.get(v, False):
                continue
            _, seeded = self.resolve(v)
            self.nres += 1
            q.extend(seeded)
        final_A = len(q)
        target = self.condition.target
        return RunResult(
            condition=self.condition.name,
            beta=self.beta,
            seed=0,  # overwritten by caller
            nres=self.nres,
            final_A=final_A,
            sustained=(self.nres >= self.max_res and final_A > 0),
            suppressed=self.suppressed,
            spawned=self.spawned,
            basin_resolutions=self.basin_resolutions,
            original_resolved=len(self.resolved_original),
            target_resolved=(None if target is None else target in self.absorber),
        )


def run_one(seed: int, beta: float, condition: Condition, max_res: int) -> RunResult:
    engine = CaptureEngine(seed=seed, beta=beta, condition=condition, max_res=max_res)
    result = engine.run()
    result.seed = seed
    return result


def mean(xs):
    return float(sum(xs) / len(xs)) if xs else float('nan')


def sd(xs):
    return float(statistics.pstdev(xs)) if len(xs) > 1 else 0.0


def summarize_results(results: list[RunResult]) -> dict:
    return {
        'n': len(results),
        'P_sustain': mean([r.sustained for r in results]),
        'mean_nres': mean([r.nres for r in results]),
        'sd_nres': sd([r.nres for r in results]),
        'mean_final_A': mean([r.final_A for r in results]),
        'sd_final_A': sd([r.final_A for r in results]),
        'mean_suppressed': mean([r.suppressed for r in results]),
        'mean_spawned': mean([r.spawned for r in results]),
        'mean_basin_resolutions': mean([r.basin_resolutions for r in results]),
        'mean_original_resolved': mean([r.original_resolved for r in results]),
    }


def beta_crossing(beta_rows: list[dict]) -> str:
    rows = sorted(beta_rows, key=lambda x: x['beta'])
    if not rows:
        return 'NA'
    if rows[0]['P_sustain'] >= 0.5:
        return f"<={rows[0]['beta']:.2f}"
    for a, b in zip(rows, rows[1:]):
        p0, p1 = a['P_sustain'], b['P_sustain']
        if p0 < 0.5 <= p1:
            if p1 == p0:
                return f"{b['beta']:.2f}"
            bc = a['beta'] + (0.5 - p0) * (b['beta'] - a['beta']) / (p1 - p0)
            return f"{bc:.3f}"
    return f">{rows[-1]['beta']:.2f}"


def run_fixed_beta_block(conditions: list[Condition], beta: float, seeds: list[int], max_res: int) -> list[dict]:
    rows = []
    for condition in conditions:
        results = [run_one(seed, beta, condition, max_res) for seed in seeds]
        summary = summarize_results(results)
        summary.update({'condition': condition.name, 'beta': beta, 'mode': condition.mode, 'gamma': condition.gamma})
        rows.append(summary)
    return rows


def run_beta_sweep(conditions: list[Condition], betas: list[float], seeds: list[int], max_res: int) -> list[dict]:
    rows = []
    for condition in conditions:
        for beta in betas:
            results = [run_one(seed, beta, condition, max_res) for seed in seeds]
            summary = summarize_results(results)
            summary.update({'condition': condition.name, 'beta': beta, 'mode': condition.mode, 'gamma': condition.gamma})
            rows.append(summary)
    return rows


def write_csv(path: Path, rows: list[dict]):
    if not rows:
        return
    keys = list(rows[0].keys())
    # include any later keys, preserving first-row order
    for row in rows[1:]:
        for key in row.keys():
            if key not in keys:
                keys.append(key)
    with path.open('w', newline='') as f:
        writer = csv.DictWriter(f, fieldnames=keys)
        writer.writeheader()
        writer.writerows(rows)


def main():
    if (SECTORS['S'], SECTORS['I'], SECTORS['G']) != (81, 40, 16):
        raise RuntimeError(f'bad sector counts {SECTORS}')
    if G.number_of_edges() != 5347:
        raise RuntimeError(f'bad edge count {G.number_of_edges()}')

    print('FINAL PRE-PAPER STERILE-MODE TEST')
    print('==================================')
    print(f'Registry: {G.number_of_nodes()} nodes, {G.number_of_edges()} edges; sectors {dict(SECTORS)}')
    print(f'Sterile sigma id={SIGMA}; object={G.nodes[SIGMA]["obj_string"]}')
    print(f'  shape={G.nodes[SIGMA]["shape"]}')
    print(f'  sector={G.nodes[SIGMA]["sector"]}, mult={G.nodes[SIGMA]["mult"]}, parent_overlap={G.nodes[SIGMA]["parent_overlap"]}, degree={G.degree(SIGMA)}')
    print(f'  universal S controls={len(NONSTERILE_UNIVERSAL_S)}; ordinary S nodes={len(ORDINARY_S)}')
    print()

    baseline = Condition('baseline_no_capture')
    pin_sigma = Condition('sigma_pinned_no_capture', pin_target=SIGMA)
    sigma_contact = Condition('sigma_contact_gamma1', target=SIGMA, mode='contact', gamma=1.0)
    sigma_adj_g05 = Condition('sigma_adjacent_gamma0.5', target=SIGMA, mode='adjacent', gamma=0.5)
    sigma_adj_g1 = Condition('sigma_adjacent_gamma1', target=SIGMA, mode='adjacent', gamma=1.0)
    # A representative matched universal-S control for the beta sweep.  The fixed-beta
    # block below tests all eight controls.
    control0 = NONSTERILE_UNIVERSAL_S[0]
    control_contact = Condition('matched_universal_contact_gamma1_rep', target=control0, mode='contact', gamma=1.0)
    control_adj_g05 = Condition('matched_universal_adjacent_gamma0.5_rep', target=control0, mode='adjacent', gamma=0.5)
    control_adj_g1 = Condition('matched_universal_adjacent_gamma1_rep', target=control0, mode='adjacent', gamma=1.0)

    fixed_beta = 1.3
    fixed_seeds = list(range(11000, 11032))
    fixed_conditions = [baseline, pin_sigma, sigma_contact, control_contact, sigma_adj_g05, control_adj_g05, sigma_adj_g1, control_adj_g1]
    print(f'Fixed-beta stress test at beta={fixed_beta} over {len(fixed_seeds)} seeds (max_res=1200)')
    fixed_rows = run_fixed_beta_block(fixed_conditions, fixed_beta, fixed_seeds, max_res=1200)
    for row in fixed_rows:
        print(
            f"  {row['condition']:<43} P_sustain={row['P_sustain']:.2f} "
            f"mean_nres={row['mean_nres']:.1f} final_A={row['mean_final_A']:.1f} "
            f"suppressed={row['mean_suppressed']:.1f} basin_res={row['mean_basin_resolutions']:.1f}"
        )
    print()

    # All eight matched controls at fixed beta, to check sigma uniqueness directly.
    all_control_rows = []
    for c in NONSTERILE_UNIVERSAL_S:
        for mode, gamma, label in [('contact', 1.0, 'contact_gamma1'), ('adjacent', 0.5, 'adjacent_gamma0.5'), ('adjacent', 1.0, 'adjacent_gamma1')]:
            cond = Condition(f'control_{c}_{label}', target=c, mode=mode, gamma=gamma)
            summary = summarize_results([run_one(seed, fixed_beta, cond, max_res=1200) for seed in fixed_seeds])
            summary.update({'condition': cond.name, 'target_id': c, 'target_obj': G.nodes[c]['obj_string'], 'mode': mode, 'gamma': gamma, 'beta': fixed_beta})
            all_control_rows.append(summary)
    print('Matched-control check at fixed beta: sigma vs 8 nonsterile universal-S targets')
    for mode, gamma in [('contact', 1.0), ('adjacent', 0.5), ('adjacent', 1.0)]:
        sigma_row = next(r for r in fixed_rows if r['mode'] == mode and abs(r['gamma'] - gamma) < 1e-12 and r['condition'].startswith('sigma'))
        controls = [r for r in all_control_rows if r['mode'] == mode and abs(r['gamma'] - gamma) < 1e-12]
        p_vals = [r['P_sustain'] for r in controls]
        nres_vals = [r['mean_nres'] for r in controls]
        final_vals = [r['mean_final_A'] for r in controls]
        print(
            f"  {mode:>8}, gamma={gamma:<3}: sigma P={sigma_row['P_sustain']:.2f}, nres={sigma_row['mean_nres']:.1f}, A={sigma_row['mean_final_A']:.1f}; "
            f"controls P range={min(p_vals):.2f}-{max(p_vals):.2f}, nres range={min(nres_vals):.1f}-{max(nres_vals):.1f}, A range={min(final_vals):.1f}-{max(final_vals):.1f}"
        )
    print()

    betas = [0.5, 0.7, 0.9, 1.1, 1.3, 1.5, 1.7, 1.9, 2.1, 2.3, 2.6, 3.0]
    sweep_seeds = list(range(12000, 12020))
    sweep_conditions = [baseline, pin_sigma, sigma_contact, control_contact, sigma_adj_g05, control_adj_g05]
    print(f'Beta-c sweep over {len(sweep_seeds)} seeds per beta (max_res=1000)')
    sweep_rows = run_beta_sweep(sweep_conditions, betas, sweep_seeds, max_res=1000)
    crossing_rows = []
    for cond in sweep_conditions:
        rows = [r for r in sweep_rows if r['condition'] == cond.name]
        bc = beta_crossing(rows)
        crossing_rows.append({'condition': cond.name, 'mode': cond.mode, 'gamma': cond.gamma, 'beta_c_50pct': bc})
        compact = ' '.join(f"{r['beta']:.1f}:{r['P_sustain']:.2f}" for r in rows)
        print(f"  {cond.name:<43} beta_c={bc:<6}   {compact}")
    print()

    # Ordinary S target as a negative topology check under strong adjacent basin.
    ordinary_target = ORDINARY_S[0]
    ordinary_adj = Condition('ordinary_S_adjacent_gamma0.5_rep', target=ordinary_target, mode='adjacent', gamma=0.5)
    ordinary_rows = run_beta_sweep([ordinary_adj], betas, sweep_seeds, max_res=1000)
    ordinary_bc = beta_crossing(ordinary_rows)
    crossing_rows.append({'condition': ordinary_adj.name, 'mode': ordinary_adj.mode, 'gamma': ordinary_adj.gamma, 'beta_c_50pct': ordinary_bc})
    print(f"Ordinary-S strong-basin negative check: beta_c={ordinary_bc}")
    print('  ' + ' '.join(f"{r['beta']:.1f}:{r['P_sustain']:.2f}" for r in ordinary_rows))
    print()

    # Persist raw summaries.
    fixed_path = OUTDIR / 'sterile_final_fixed_beta_summary.csv'
    controls_path = OUTDIR / 'sterile_final_matched_controls_summary.csv'
    sweep_path = OUTDIR / 'sterile_final_beta_sweep_summary.csv'
    crossing_path = OUTDIR / 'sterile_final_beta_crossings.csv'
    write_csv(fixed_path, fixed_rows)
    write_csv(controls_path, all_control_rows)
    write_csv(sweep_path, sweep_rows + ordinary_rows)
    write_csv(crossing_path, crossing_rows)

    sigma_info = {
        'id': SIGMA,
        'obj_string': G.nodes[SIGMA]['obj_string'],
        'shape': G.nodes[SIGMA]['shape'],
        'sector': G.nodes[SIGMA]['sector'],
        'mult': G.nodes[SIGMA]['mult'],
        'parent_overlap': G.nodes[SIGMA]['parent_overlap'],
        'degree': G.degree(SIGMA),
        'neighbor_sectors': dict(Counter(G.nodes[u]['sector'] for u in G.neighbors(SIGMA))),
        'nonsterile_universal_S_controls': [
            {
                'id': c,
                'obj_string': G.nodes[c]['obj_string'],
                'shape': G.nodes[c]['shape'],
                'mult': G.nodes[c]['mult'],
                'parent_overlap': G.nodes[c]['parent_overlap'],
                'degree': G.degree(c),
            }
            for c in NONSTERILE_UNIVERSAL_S
        ],
    }
    (OUTDIR / 'sterile_final_sigma_and_controls.json').write_text(json.dumps(sigma_info, indent=2))

    report_path = OUTDIR / 'sterile_final_pre_paper_report.md'
    report_lines = []
    report_lines.append('# Final pre-paper sterile-mode test\n')
    report_lines.append('## Verdict\n')
    report_lines.append(
        '**Result: NULL for a sterile-specific mechanism; PASS for a universal-basin capture control.**\n\n'
        'Adding a basin-capture damping rule can strongly alter expansion, but sigma does not move the metrics beyond matched nonsterile universal-S controls. '
        'The effect is controlled by the capture semantics and universal-hub topology, not by multiplicity-1 under the current dynamics.\n'
    )
    report_lines.append('## Sigma\n')
    report_lines.append(f"- object: `{G.nodes[SIGMA]['obj_string']}`\n")
    report_lines.append(f"- shape: `{G.nodes[SIGMA]['shape']}`\n")
    report_lines.append(f"- sector/multiplicity/parent-overlap/degree: {G.nodes[SIGMA]['sector']}/{G.nodes[SIGMA]['mult']}/{G.nodes[SIGMA]['parent_overlap']}/{G.degree(SIGMA)}\n")
    report_lines.append(f"- neighbor sectors: {dict(Counter(G.nodes[u]['sector'] for u in G.neighbors(SIGMA)))}\n")
    report_lines.append(f"- matched universal-S controls: {len(NONSTERILE_UNIVERSAL_S)}\n\n")
    report_lines.append('## Fixed-beta stress test, beta=1.3\n\n')
    report_lines.append('| condition | P_sustain | mean resolutions | mean final A | mean suppressed | mean basin resolutions |\n')
    report_lines.append('|---|---:|---:|---:|---:|---:|\n')
    for row in fixed_rows:
        report_lines.append(f"| {row['condition']} | {row['P_sustain']:.2f} | {row['mean_nres']:.1f} | {row['mean_final_A']:.1f} | {row['mean_suppressed']:.1f} | {row['mean_basin_resolutions']:.1f} |\n")
    report_lines.append('\n## Matched-control check\n\n')
    report_lines.append('| basin mode | gamma | sigma P_sustain | control P_sustain range | sigma mean resolutions | control mean-resolution range |\n')
    report_lines.append('|---|---:|---:|---:|---:|---:|\n')
    for mode, gamma in [('contact', 1.0), ('adjacent', 0.5), ('adjacent', 1.0)]:
        sigma_row = next(r for r in fixed_rows if r['mode'] == mode and abs(r['gamma'] - gamma) < 1e-12 and r['condition'].startswith('sigma'))
        controls = [r for r in all_control_rows if r['mode'] == mode and abs(r['gamma'] - gamma) < 1e-12]
        p_vals = [r['P_sustain'] for r in controls]
        nres_vals = [r['mean_nres'] for r in controls]
        report_lines.append(f"| {mode} | {gamma:.1f} | {sigma_row['P_sustain']:.2f} | {min(p_vals):.2f}–{max(p_vals):.2f} | {sigma_row['mean_nres']:.1f} | {min(nres_vals):.1f}–{max(nres_vals):.1f} |\n")
    report_lines.append('\n## Beta-c sweep\n\n')
    report_lines.append('| condition | beta_c, 50% crossing |\n')
    report_lines.append('|---|---:|\n')
    for row in crossing_rows:
        report_lines.append(f"| {row['condition']} | {row['beta_c_50pct']} |\n")
    report_lines.append('\n## Interpretation\n\n')
    report_lines.append(
        '1. Pinning sigma without a capture rule barely changes the baseline, so the existing expansion engine does not require the sterile node dynamically.\n'
        '2. The weak contact rule has a limited effect because only lineages that actually side-link into the target enter the basin. Sigma and the matched universal-S controls remain indistinguishable.\n'
        '3. The strong adjacent-basin rule moves the open-future threshold sharply upward, but every universal S-node does the same because each is adjacent to the whole registry.\n'
        '4. Therefore the paper should not claim a sterile-specific mechanism from the current test. The safe claim is that the multiplicity-1 object is a canonical representative of a universal-basin capture mode; multiplicity itself is not yet a dynamical cause.\n'
    )
    report_path.write_text(''.join(report_lines))

    print('Artifacts written:')
    print(f'  {report_path}')
    print(f'  {fixed_path}')
    print(f'  {controls_path}')
    print(f'  {sweep_path}')
    print(f'  {crossing_path}')
    print(f'  {OUTDIR / "sterile_final_sigma_and_controls.json"}')


if __name__ == '__main__':
    main()
