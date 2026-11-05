# per-tick static account of R_vm, MMD-CS (counts: probe 0291 / 1000 ticks)
HEAD={0:19,1:22,2:20}; BACK=5
movl_h=(417*34+43*40+64*37+28*40+204*69)/756
rows=[ # name, count/tick, argc, handler instrs (incl. its tail), note
('mov',813.2,2,19,'20-byte reg copy'),
('movl',722.3,2,movl_h,'fixup switch + 2x20-byte copy; import path calls GetByIndex'),
('subi MAR walk',429.6,2,7+6+16+6*1143.9/429.6,'GetStackPtrOffsetRw inlined, 2.66 steps'),
('subi SP free',66.0,2,45,'PopDataFromStack (est.)'),
('subi plain',58.9,2,13,''),
('sourceline',550.5,1,9,'no hook'),
('memread4 stack/global',424.6,1,29,'type switch + 20-byte write'),
('memread4 object',28.0,1,65,'virtual ReadInt32 (est.)'),
('memread4 staticarr',1.0,1,65,''),
('push',383.6,1,53,'stack-space checks + SP type switch + 20-byte write'),
('pop',298.7,1,42,'copy to temp, zero entry, copy to reg'),
('farpush',288.7,1,23,''),
('jzi',182.8,1,11,''),
('farcall (R_vm part)',174.8,1,12,'post-API tail only; the rest is R_marsh/R_api'),
('setfuncargs',174.8,1,5,''),
('farsubsp',167.8,1,28,''),
('cmpeq',125.9,2,21,''),('sub',95.9,2,12,''),('addi',90.9,2,11,''),
('memwrite4',86.9,1,25,'type switch + write (est.)'),
('ret',65.9,0,38,''),('thisaddr',65.9,1,6,''),('gte',64.9,2,17,''),
('call',63.9,1,61,'plus a full Run entry, below'),
('add',56.9,2,11,''),('jmpi',49.0,1,8,''),('memwritelit',33.0,2,45,'(est.)'),
('muli',28.0,2,9,''),('memread1',14.0,1,39,'ReadByte call'),('memwrite1',14.0,1,37,'WriteByte call'),
('land',8.0,2,23,''),('lor',6.0,2,24,''),('cmpne',5.0,2,21,''),('lt',2.0,2,17,''),('gt',1.0,2,17,''),
]
tot_ops=0; tot_ovh=0; tot_h=0
out=[]
for n,c,a,h,note in rows:
    ov=(HEAD[a]+BACK)*c; hh=h*c
    tot_ovh+=ov; tot_h+=hh; out.append((n,c,a,h,ov+hh,note))
ops=sum(r[1] for r in rows)-429.6-66.0-58.9+554.4-424.6-28-1+453.5  # de-dup the split rows
runs=65; per_run=110+250+70+169+15
run_cost=runs*per_run
total=tot_ovh+tot_h+run_cost
for n,c,a,h,t,note in sorted(out,key=lambda r:-r[4]): print(f'{n:22s} {c:6.0f}/tick argc{a} handler {h:5.1f}  total {t/1000:6.1f}k  {note}')
print(f'\nops/tick counted {sum(r[1] for r in rows):.0f} (all 31 opcodes MMD-CS executes)')
print(f'loop head+back-edge {tot_ovh/1000:.1f}k | handlers {tot_h/1000:.1f}k | Run entries {runs} x {per_run} = {run_cost/1000:.1f}k')
print(f'TOTAL {total/1000:.1f}k instr/tick = {total/40000:.2f} ms at 40k/ms ; measured R_vm ~7.7 ms = 308k')
print(f'residual {(308000-total)/1000:.1f}k = {(308000-total)/40000:.2f} ms ({(308000-total)/308000*100:.0f}%)')
