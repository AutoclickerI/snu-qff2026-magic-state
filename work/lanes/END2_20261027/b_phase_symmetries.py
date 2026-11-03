"""Exact single-clock local-S symmetries in the actual B45 resource schedule.

Computational support is propagated from official source-product certificates.
Every emitted pulse fixes that entire support, irrespective of state amplitudes
or recorded X signs. Complete noisy circuit scoring is deliberately separate.
"""
import hashlib
import itertools
import json
import argparse
from pathlib import Path
from source_product_boundaries import HERE, ROOT, f, certify

MODULE=HERE.parent/'PREFIX2_20261027/retimed/b45_alap_b_module.json'
FULL=HERE.parent/'EXPAND2_20261027/b_phase/before_check_none_41980dcd56d63cbb_d6_20_19_10_2_22_16'


def solve_binary(vectors,target):
    piv={}
    for index,value in enumerate(vectors):
        combo=1<<index
        while value:
            bit=value.bit_length()-1
            if bit not in piv:
                piv[bit]=(value,combo);break
            other,mask=piv[bit];value^=other;combo^=mask
    combo=0
    while target:
        bit=target.bit_length()-1
        if bit not in piv:return None
        value,mask=piv[bit];target^=value;combo^=mask
    return combo


def labels_for(columns):
    basis=[]
    for value in sorted(set(columns.values())):
        if value and solve_binary(basis,value) is None:basis.append(value)
    labels={q:solve_binary(basis,value) for q,value in columns.items()}
    assert all(value is not None for value in labels.values())
    return basis,labels


def feature(label,rank):
    result=0;offset=0
    for i in range(rank):
        for j in range(i,rank):
            result|=((label>>i&1)&(label>>j&1))<<offset;offset+=1
    return result


def generate(module_path=MODULE,full_stem=FULL,output_dir=HERE,output_prefix='b_phase',check_shift=1,start=None,end=None,product_states=None,source_prefix=None):
    module_path=Path(module_path);full_stem=Path(full_stem);output_dir=Path(output_dir)
    output_dir.mkdir(parents=True,exist_ok=True)
    module=json.loads(module_path.read_text());source=Path(source_prefix or module['prefix_stem'])
    source_ops,_=f.parse_current(source.with_suffix('.qasm').read_text())
    data=module['roles']['D']
    release={q:max((op.time+1 for op in source_ops if q in op.qs),default=0)
             for q in range(36) if q not in data}
    certificate=output_dir/f'{output_prefix}_product_states.json'
    receipt=output_dir/f'{output_prefix}_source_receipt.json'
    receipt.write_text(json.dumps(dict(stem=str(source),release=release,data_qubits=data),indent=2)+'\n')
    if product_states:
        certificate=Path(product_states);products=json.loads(certificate.read_text())
    else:products=certify(receipt,certificate)
    states={row['q']:row for row in products['cells']}
    bops=[dict(op) for op in module['candidates'][0]['operations']]
    B,C=module['roles']['B'],module['roles']['C']
    last_check=max(op['time'] for op in bops if op['kind']=='CX' and tuple(op['qs']) in set(zip(B,C)))
    for op in bops:
        if op['kind']=='CX' and op['time']==last_check and tuple(op['qs']) in set(zip(B,C)):op['time']+=check_shift
        elif op['kind']=='M' and op['time']==last_check+1 and op['qs'][0] in C:op['time']+=check_shift
    bops.sort(key=lambda op:op['time'])
    cells=sorted({q for op in bops for q in op['qs']})
    full_ops,_=f.parse_current(full_stem.with_suffix('.qasm').read_text())
    occupied={(op.time,q) for op in full_ops for q in op.qs}
    full_keys={(op.kind,tuple(op.qs),op.time) for op in full_ops}
    for op in bops:
        assert (op['kind'],tuple(op['qs']),op['time']) in full_keys,op
    # Certifying the source separately is legitimate only when its actual
    # operations on the resource wires match the requested complete circuit.
    for op in source_ops:
        if set(op.qs)&set(cells):assert (op.kind,tuple(op.qs),op.time) in full_keys,('source mismatch',op)
    start=min(op['time'] for op in bops) if start is None else start
    end=max(op['time'] for op in bops)-1 if end is None else end
    columns={};next_variable=0;classical_variables={};zero_reads=[];nonzero_reads=[];snapshots=[]
    primary=[];composite=[];zero=[]

    def fresh():
        nonlocal next_variable
        value=1<<next_variable;next_variable+=1;return value

    for tick in range(max(op['time'] for op in bops)+1):
        for q in cells:
            if q in columns or release[q]!=tick:continue
            row=states[q]
            assert row['product_axis'] in ('X','Z') and row['phase_constant']==0,row
            if row['product_axis']=='Z':
                columns[q]=0
                for record in row['phase_xor']:
                    if record not in classical_variables:classical_variables[record]=fresh()
                    columns[q]^=classical_variables[record]
            else:columns[q]=fresh()
        if start<=tick<=end:
            basis,labels=labels_for(columns);rank=len(basis)
            idle=[q for q in cells if q in columns and (tick,q) not in occupied]
            zeros=[q for q in idle if labels[q]==0]
            nonzero=[q for q in idle if labels[q]!=0]
            snapshot=dict(time=tick,rank=rank,columns=labels,raw_columns=dict(columns),basis=basis,idle=idle,
                          zero_columns=zeros,nonzero_idle=nonzero)
            snapshots.append(snapshot)
            for q in zeros:
                zero.append(dict(name=f't{tick:02d}_zero_{q}',operations=[dict(kind='S',qs=[q],time=tick)],
                    family='zero_column',proof=dict(column=0,all_support_phases_mod4=[0]),
                    equivalent_sign='SDG fixes the same state and has identical Pauli-axis action up to sign.',
                    noise_equivalent_on_pauli_images_of_ideal_support=True,
                    full_source_all_orders_noise_equivalence_proved=False,
                    note='A zero computational column is a Z stabilizer. Local S acts only by global phase on each Pauli image of the ideal support, and its depolarizing channel matches an active idle. This is not by itself an all-orders equivalence proof for coherent source errors propagated through non-Clifford gates.'))
            feats=[feature(labels[q],rank) for q in nonzero]
            signatures=[0]*(1<<len(nonzero))
            for mask in range(1,1<<len(nonzero)):
                bit=mask&-mask;index=bit.bit_length()-1
                signatures[mask]=signatures[mask^bit]^feats[index]
                if signatures[mask]:continue
                selected=[q for i,q in enumerate(nonzero) if mask>>i&1]
                selected_labels=[labels[q] for q in selected]
                # The diagonal Clifford phase polynomial has only linear and
                # quadratic terms modulo4. Vanishing Gram features remove all
                # quadratic terms; signs below cancel the remaining linear part.
                target=sum(((sum(v>>i&1 for v in selected_labels)//2)&1)<<i for i in range(rank))
                minus=solve_binary(selected_labels,target)
                assert minus is not None
                family='composite_symmetry'
                if len(selected)==2 and selected_labels[0]==selected_labels[1]:family='identical_column_pair'
                elif len(selected)==7 and len(set(selected_labels))==7:
                    flat_basis,flat=labels_for(dict(enumerate(selected_labels)))
                    if len(flat_basis)==3 and set(flat.values())==set(range(1,8)):
                        family='seven_nonzero_columns';minus=0
                signs=[-1 if minus>>i&1 else 1 for i in range(len(selected))]
                phases=[sum(sign*((label&word).bit_count()&1) for sign,label in zip(signs,selected_labels))%4
                        for word in range(1<<rank)]
                assert set(phases)=={0},(tick,selected,signs,phases)
                ops=[dict(kind='SDG' if sign<0 else 'S',qs=[q],time=tick) for q,sign in zip(selected,signs)]
                name=f't{tick:02d}_'+('pair' if family=='identical_column_pair' else 'seven' if family=='seven_nonzero_columns' else 'combo')+'_'+'_'.join(map(str,selected))
                candidate=dict(name=name,operations=ops,family=family,
                    proof=dict(rank=rank,columns={q:labels[q] for q in selected},signs=signs,
                               all_support_phases_mod4=phases,
                               phase_polynomial='sum(sign_q * parity(column_q & u)) ==0 mod4 for every support wordu'),
                    occupied_slots_checked=True,source_leases_checked=True,
                    sign_quotient='Other valid S/SDG signs on this same support differ by a Z stabilizer; they have identical Pauli-axis action and are not duplicated.')
                (primary if family!='composite_symmetry' else composite).append(candidate)
        for op in (op for op in bops if op['time']==tick):
            kind=op['kind'];qs=op['qs']
            assert all(q in columns for q in qs),(op,release)
            if kind=='CX':columns[qs[1]]^=columns[qs[0]]
            elif kind=='R':columns[qs[0]]=0
            elif kind=='RX':columns[qs[0]]=fresh()
            elif kind=='M':
                item=dict(time=tick,q=qs[0],column=columns[qs[0]],original_bit=op.get('original_bit'))
                (zero_reads if columns[qs[0]]==0 else nonzero_reads).append(item)
            elif kind=='MX':
                q=qs[0];others=[v for k,v in columns.items() if k!=q]
                if columns[q]==0 or solve_binary(others,columns[q]) is not None:columns[q]=fresh()
            else:raise ValueError(op)
    if nonzero_reads:
        # Treating a classical source record as an independent support variable
        # is a conservative unconditional-support model. A Z measurement does
        # not change that support, so it need not be a literal zero in this case.
        assert classical_variables,nonzero_reads
    common=dict(full_stem=str(full_stem),b_module=str(module_path),source_prefix=str(source),
        full_qasm_sha256=hashlib.sha256(full_stem.with_suffix('.qasm').read_bytes()).hexdigest(),
        source_product_certificate=str(certificate),time_range=[start,end],cells=cells,
        ideal_scope='Exact computational-support identity on all certified source-product branches. Arbitrary amplitudes and recorded X signs are allowed; no perfect gate or postselection change is introduced.',
        noise_scope='All added S/SDG pulses are real noisy native gates; root must full-audit and score each circuit.',
        completeness='All pulse supports on nonzero idle columns were enumerated by the binary Gram condition. One valid S/SDG sign representative is retained per support, quotienting Z-stabilizer-equivalent choices. Zero-column factors are factored out; their individual placements are in the separate zero file. Primary file contains the requested pair and seven-column families; remaining combined supports are in the composite file. No retiming, multiple-clock patterns, SX/H gates, unleased cells, or new postselection is included.',
        zero_measurements=zero_reads,nonzero_support_measurements=nonzero_reads,
        classical_records_promoted_to_support_variables=classical_variables,
        classical_scope='Strict global identity over all source-record sectors. Conditional global phases and known conditional-Z byproducts require the separate affine enumerator.')
    for suffix,candidates in [('candidates',primary),('composite_candidates',composite),('zero_candidates',zero)]:
        (output_dir/f'{output_prefix}_{suffix}.json').write_text(json.dumps(dict(**common,candidates=candidates),indent=2)+'\n')
    inventory=dict(**common,snapshots=snapshots,counts=dict(primary=len(primary),composite=len(composite),zero=len(zero)))
    (output_dir/f'{output_prefix}_columns.json').write_text(json.dumps(inventory,indent=2)+'\n')
    print(json.dumps(dict(counts=inventory['counts'],primary_by_time={t:sum(c['operations'][0]['time']==t for c in primary) for t in range(start,end+1)},
                         rank_by_time={r['time']:r['rank'] for r in snapshots})),flush=True)
    return inventory


if __name__=='__main__':
    ap=argparse.ArgumentParser(description=__doc__)
    ap.add_argument('--module',default=str(MODULE));ap.add_argument('--base-stem',default=str(FULL))
    ap.add_argument('--output-dir',default=str(HERE));ap.add_argument('--output-prefix',default='b_phase')
    ap.add_argument('--check-shift',type=int,default=1);ap.add_argument('--start',type=int);ap.add_argument('--end',type=int)
    ap.add_argument('--product-states');ap.add_argument('--source-prefix')
    args=ap.parse_args();generate(args.module,args.base_stem,args.output_dir,args.output_prefix,args.check_shift,args.start,args.end,args.product_states,args.source_prefix)
