from pathlib import Path
H=Path(__file__).resolve().parent;D=H/'a35/exenc';s=(D/'exact_original.cpp').read_text().replace('#include <functional>','#include <functional>\n#include <fstream>')
s=s.replace('bool better(const Circuit& a,const Circuit& b) {','int blind(const Circuit& c) {return c.vec[3]+c.vec[4]+c.vec[7];}\nvoid write_circuit(const Circuit& c,ostream& output);\nbool better(const Circuit& a,const Circuit& b) {').replace('tuple(a.units,a.layers.size(),a.cx,a.pivots,a.layers)','tuple(blind(a),a.units-blind(a),a.layers.size(),a.cx,a.pivots,a.layers)').replace('tuple(b.units,b.layers.size(),b.cx,b.pivots,b.layers)','tuple(blind(b),b.units-blind(b),b.layers.size(),b.cx,b.pivots,b.layers)')
start=s.index('void write_circuit(const Circuit& c) {');end=s.index('\nint main()',start);body=s[start:end].replace('void write_circuit(const Circuit& c) {','void write_circuit(const Circuit& c,ostream& output=cout) {').replace('cout<<','output<<');s=s[:start]+body+s[end:]
extra=r'''
// Pareto metrics are a local proxy only. No intermediate ideal-state winner
// pruning is used; every canonical path is scored. Every path fitting the
// actual v35b release/deadline geometry is exported even when proxy-dominated.
using PKey=array<int,4>; // blind, detected, CX, depth
bool dominates(const PKey&a,const PKey&b) {
 bool strict=false;for(int j=0;j<4;j++){if(a[j]>b[j])return false;strict|=a[j]<b[j];}return strict;
}
bool native_fit(const Circuit& c,Circuit& out,int& start) {
 vector<int> flat;for(auto& layer:c.layers)for(int e:layer)flat.push_back(e);
 array<int,36> nxt,first;first.fill(1000);nxt.fill(44);
 for(int q=0;q<n;q++)if(avail[q]==9||avail[q]==15)nxt[q]=43;
 vector<int> times(flat.size());
 for(int j=int(flat.size())-1;j>=0;j--){auto[u,v]=edges[flat[j]];int t=min(nxt[u],nxt[v])-1;times[j]=t;nxt[u]=nxt[v]=t;first[u]=first[v]=t;}
 auto release=[](int q){if(q==8)return 35;if(q==16)return 36;if(q==15)return 39;return 37;};
 for(int q=0;q<n;q++){
  bool was_plus=avail[q]==2||avail[q]==14;
  bool plus=find(c.pivots.begin(),c.pivots.end(),q)!=c.pivots.end();
  if(first[q]<release(avail[q])+1+int(was_plus!=plus))return false;
 }
 start=*min_element(times.begin(),times.end());int finish=*max_element(times.begin(),times.end());
 out.pivots=c.pivots;out.layers.resize(finish-start+1);
 for(size_t j=0;j<flat.size();j++)out.layers[times[j]-start].push_back(flat[j]);
 for(auto& layer:out.layers)sort(layer.begin(),layer.end());score(out);return true;
}
'''
s=s.replace('struct Collector {',extra+'\nstruct Collector {\n    map<PKey,vector<Circuit>> pareto;\n    ofstream feasible;\n    U feasible_count=0;\n    void add_pareto(const Circuit& c) {\n        PKey key{blind(c),c.units-blind(c),c.cx,int(c.layers.size())};\n        for(auto&[k,v]:pareto)if(dominates(k,key))return;\n        for(auto it=pareto.begin();it!=pareto.end();)if(dominates(key,it->first))it=pareto.erase(it);else ++it;\n        pareto[key].push_back(c);\n    }')
s=s.replace('        score(c);\n        auto& s=stats',r'''        score(c);add_pareto(c);
        if(mode==0) {Circuit nc;int start;if(native_fit(c,nc,start)) {
            feasible_count++;feasible<<"{\"start\":"<<start<<",\"blind\":"<<blind(nc)<<",\"detected\":"<<nc.units-blind(nc)<<",\"circuit\":";write_circuit(nc,feasible);feasible<<"}\n";
        }}
        auto& s=stats''')
s=s.replace('    for(int w=0;w<workers;w++) threads.emplace_back', '    for(int w=0;w<workers;w++) collectors[w].feasible.open("native_paths_"+to_string(w)+".jsonl");\n    for(int w=0;w<workers;w++) threads.emplace_back')
s=s.replace('    for(int w=0;w<workers;w++) {\n        for(int d=0;', '    for(int w=0;w<workers;w++) {\n        collectors[w].feasible.close();\n        for(auto&[key,cs]:collectors[w].pareto)for(auto& c:cs)merged.add_pareto(c);\n        for(int d=0;')
s=s.replace('    sort(merged.top.begin()', '    ofstream pf("pareto_paths.jsonl");\n    for(auto&[key,cs]:merged.pareto)for(auto& c:cs){pf<<"{\\\"blind\\\":"<<key[0]<<",\\\"detected\\\":"<<key[1]<<",\\\"cx\\\":"<<key[2]<<",\\\"depth\\\":"<<key[3]<<",\\\"circuit\\\":";write_circuit(c,pf);pf<<"}\\n";}\n    pf.close();\n    sort(merged.top.begin()')
(D/'exact_flag.cpp').write_text(s)
