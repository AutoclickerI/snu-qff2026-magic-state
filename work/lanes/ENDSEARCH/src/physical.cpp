#define main encoded_main
#include "search.cpp"
#undef main
#include <cstdint>
#include <unordered_map>
using U=uint64_t;
struct PB {U p[40]={};void add(U x){for(int j=39;j>=0;j--)if(x>>j&1){if(p[j])x^=p[j];else{p[j]=x;return;}}}bool has(U x){for(int j=39;j>=0;j--)if(x>>j&1){if(p[j])x^=p[j];else return false;}return !x;}};
struct PR {vector<int>types;vector<pair<int,int>>bells;};vector<PR>pres;
U block(int b,int mask=127){return U(mask)<<(7*b);}int pg[3]={85,102,120};
void resources_phys(int q,PR r){while(q<n&&r.types[q]>=0)q++;if(q==n){pres.push_back(r);return;}for(int t=0;t<6;t++){auto s=r;s.types[q]=t;resources_phys(q+1,s);}for(int b=q+1;b<n;b++)if(r.types[b]<0){auto s=r;s.types[q]=s.types[b]=6;s.bells.push_back({q,b});resources_phys(q+1,s);}}
U transform(U x,bool z){for(int tt:seq)for(auto[a,b]:layers[tt]){if(z)swap(a,b);U v=(x>>(7*a))&127;x^=v<<(7*b);}return x;}
bool instrument(vector<U>s,U measured,U corr,vector<U>&ds,U&frame){U piv[40]={};for(U row:s){U v=row&~measured;for(int j=39;j>=0;j--)if(v>>j&1){if(piv[j]){row^=piv[j];v=row&~measured;}else{piv[j]=row;break;}}if(!(row&~measured)&&row)ds.push_back(row);}
 U out=corr;for(int j=39;j>=0;j--)if((out&~measured)>>j&1){if(!piv[j])return false;out^=piv[j];}frame=out&measured;return !(out&~measured);}
int syn(int v){int s=0;for(int i=0;i<7;i++)if(v>>i&1)s^=i+1;return s;}
int rank32(vector<int>vs){uint32_t p[32]={};int r=0;for(uint32_t v:vs)for(int j=31;j>=0;j--)if(v>>j&1){if(p[j])v^=p[j];else{p[j]=v;r++;break;}}return r;}
double loss8(int e){int fz=((e>>6)&1)^bool(e&7),fx=((e>>7)&1)^bool(e&56);return (2-(fz?-1:1)-((fx^fz)?-1:1))/4.;}
struct PF{uint32_t d;int e,w,chan;};
long long pschedules=0,presources=0,pinstruments=0,pvalid=0,pft=0;
map<string,vector<Winner>> pbest;
string uvec(vector<U>v){ostringstream o;o<<'[';for(int j=0;j<(int)v.size();j++)o<<(j?",":"")<<v[j];o<<']';return o.str();}
void physical(){if(!canon())return;pschedules++;int last[5];fill(last,last+n,-1);bool adj[5][5]={};int deg[5]={};for(int t=0;t<depth;t++)for(auto[a,b]:layers[seq[t]]){last[a]=last[b]=t;adj[a][b]=adj[b][a]=true;}int reach=1;for(int i=0;i<n;i++)for(int a=0;a<n;a++)if(reach>>a&1)for(int b=0;b<n;b++)if(adj[a][b])reach|=1<<b;if(reach!=(1<<n)-1)return;int edges=0;for(int a=0;a<n;a++)for(int b=a+1;b<n;b++)if(adj[a][b])edges++,deg[a]++,deg[b]++;string graph=edges==n-1?"tree":edges==n&&*max_element(deg,deg+n)==2?"cycle":"hops";
 struct TF{int x,z,w,q,t;};vector<TF> ff;vector<int> fc;int cid=0;for(int t=0;t<depth;t++){int used=0;for(auto[a,b]:layers[seq[t]]){used|=(1<<a)|(1<<b);for(int pa=0;pa<4;pa++)for(int pb=0;pb<4;pb++)if(pa||pb){auto q=propagate(((pa&1)<<a)|((pb&1)<<b),(((pa>>1)&1)<<a)|(((pb>>1)&1)<<b),t);ff.push_back({q.first,q.second,1,-1,t});fc.push_back(cid);}cid++;}for(int q=0;q<n;q++)if(!(used>>q&1)){for(int p=1;p<4;p++){auto v=propagate((p&1)<<q,((p>>1)&1)<<q,t);ff.push_back({v.first,v.second,5,q,t});fc.push_back(cid);}cid++;}}
 for(auto r:pres){presources++;vector<U>xs,zs;for(int g:pg){xs.push_back(block(0,g));zs.push_back(block(0,g));}xs.push_back(block(0)|(U(1)<<(7*n)));zs.push_back(block(0)|(U(1)<<(7*n)));
 for(int b=1;b<n;b++){int t=r.types[b];if(t<2){for(int g:pg){xs.push_back(block(b,g));zs.push_back(block(b,g));}(t==1?xs:zs).push_back(block(b));}else if(t<4){for(int i=0;i<7;i++)(t==3?xs:zs).push_back(block(b,1<<i));}else if(t<6){(t==4?xs:zs).push_back(block(b));for(int i=1;i<7;i++)(t==4?zs:xs).push_back(block(b,1|(1<<i)));}}
 for(auto[a,b]:r.bells)for(int i=0;i<7;i++){xs.push_back(block(a,1<<i)|block(b,1<<i));zs.push_back(block(a,1<<i)|block(b,1<<i));}
 for(U&v:xs)v=transform(v,false);for(U&v:zs)v=transform(v,true);PB bx,bz;for(U v:xs)bx.add(v);for(U v:zs)bz.add(v);bool good=true;for(int g:pg)if(!bx.has(block(0,g))||!bz.has(block(0,g)))good=false;if(!good)continue;
 int modes=1;for(int b=1;b<n;b++)modes*=3;for(int m=0;m<modes;m++){pinstruments++;int k=m,mx=0,mz=0;U X=0,Z=0;bool extra=false;for(int b=1;b<n;b++){int v=k%3;k/=3;if(v){if(last[b]==depth-1)extra=true;if(v==1)mx|=1<<b,X|=block(b);else mz|=1<<b,Z|=block(b);}}
 vector<U>ds;U fx=0,fz=0,corr=block(0)|(U(1)<<(7*n));if(!instrument(xs,X,corr,ds,fz)||!instrument(zs,Z,corr,ds,fx))continue;PB bd;vector<U>dets;for(U d:ds)if(!bd.has(d)){bd.add(d);dets.push_back(d);}auto sig=[&](int x,int z,int i){U rec=0;for(int b=1;b<n;b++)if(((x>>b&1)&&(mz>>b&1))||((z>>b&1)&&(mx>>b&1)))rec|=U(1)<<(7*b+i);uint32_t d=0;for(int j=0;j<(int)dets.size();j++)if(__builtin_parityll(rec&dets[j]))d|=1u<<j;int ox=(x&1)?1<<i:0,oz=(z&1)?1<<i:0;if(__builtin_parityll(fx&rec))ox^=127;if(__builtin_parityll(fz&rec))oz^=127;return pair{d,syn(oz)|(syn(ox)<<3)|(parity(oz)<<6)|(parity(ox)<<7)};};
 vector<int>boundary;for(int i=0;i<7;i++)for(int p:{1,2}){auto v=propagate(p&1,(p>>1)&1,-1);boundary.push_back(sig(v.first,v.second,i).first);}if(rank32(boundary)!=6)continue;pvalid++;
 vector<PF>fs;for(int i=0;i<7;i++){for(int j=0;j<(int)ff.size();j++){if(ff[j].q>=0 && ((mx|mz)>>ff[j].q&1) && ff[j].t>last[ff[j].q])continue;auto v=sig(ff[j].x,ff[j].z,i);fs.push_back({v.first,v.second,ff[j].w,fc[j]+i*(cid+10)});}for(int b=1;b<n;b++)if((mx|mz)>>b&1){auto v=sig((mz>>b&1)?1<<b:0,(mx>>b&1)?1<<b:0,i);fs.push_back({v.first,v.second,15,cid+b+i*(cid+10)});}if(extra)for(int p=1;p<4;p++){auto v=sig(p&1,(p>>1)&1,i);fs.push_back({v.first,v.second,5,cid+7+i*(cid+10)});}}
 double c1=0;for(auto f:fs)if(!f.d)c1+=f.w*loss8(f.e);if(c1>1e-10)continue;pft++;
 unordered_map<uint32_t,map<int,double>> groups;unordered_map<int,vector<PF>>channels;for(auto f:fs){groups[f.d][f.e]+=f.w;channels[f.chan].push_back(f);}double c2=0;for(auto &[d,es]:groups)for(auto [e,w]:es)for(auto [f,v]:es)c2+=w*v*loss8(e^f)/2;for(auto &[ch,vs]:channels)for(auto a:vs)for(auto b:vs)if(a.d==b.d)c2-=a.w*b.w*loss8(a.e^b.e)/2;c2/=225;
 int partner=-1;for(auto[a,b]:layers[seq[depth-1]])if(a==0)partner=b;else if(b==0)partner=a;string term=!extra&&partner>=0&&!((mx|mz)>>partner&1)?"unmeasured":"idle";string key=to_string(n)+"/"+graph+"/"+term;auto&vv=pbest[key];bool duplicate=false;for(auto w:vv)if(abs(w.cost-c2)<1e-8)duplicate=true;if(duplicate||(vv.size()>=3&&c2>=vv.back().cost))continue;
 ostringstream o;o.precision(17);o<<"{\"physical_resource\":true,\"n\":"<<n<<",\"depth\":"<<depth<<",\"output\":0,\"layers\":[";for(int t=0;t<depth;t++){if(t)o<<',';o<<'[';for(int j=0;j<(int)layers[seq[t]].size();j++){auto[a,b]=layers[seq[t]][j];if(j)o<<',';o<<'['<<a<<','<<b<<']';}o<<']';}o<<"],\"types\":"<<jvec(r.types)<<",\"bell_pairs\":[";for(int j=0;j<(int)r.bells.size();j++){if(j)o<<',';o<<'['<<r.bells[j].first<<','<<r.bells[j].second<<']';}o<<"],\"read_x\":"<<mx<<",\"read_z\":"<<mz<<",\"physical_frame_x\":"<<fx<<",\"physical_frame_z\":"<<fz<<",\"physical_detectors\":"<<uvec(dets)<<",\"graph\":\""<<graph<<"\",\"terminal\":\""<<term<<"\",\"second_order_p2\":"<<c2<<",\"first_order\":0,\"incoming_syndrome_rank\":6}";vv.push_back({c2,o.str()});sort(vv.begin(),vv.end(),[](auto a,auto b){return a.cost<b.cost;});if(vv.size()>3)vv.pop_back();
 }
 }
}
int main(int argc,char**argv){n=stoi(argv[1]);int dm=stoi(argv[2]);makelayers((1<<n)-1,{});sort(layers.begin(),layers.end());layers.erase(unique(layers.begin(),layers.end()),layers.end());vector<int>p(n);for(int i=0;i<n;i++)p[i]=i;do{perms.push_back(p);}while(next_permutation(p.begin()+1,p.end()));PR rr;rr.types=vector<int>(n,-1);rr.types[0]=0;resources_phys(1,rr);
 for(depth=2;depth<=dm;depth++){seq.resize(depth);function<void(int)>go=[&](int t){if(t==depth){physical();return;}for(int i=0;i<(int)layers.size();i++){seq[t]=i;go(t+1);}};go(0);cerr<<"n "<<n<<" d "<<depth<<" schedules "<<pschedules<<" resources "<<presources<<" instruments "<<pinstruments<<" valid "<<pvalid<<" FT "<<pft<<endl;}
 for(auto[key,vs]:pbest)for(auto w:vs)cout<<w.row<<'\n';cerr<<"COUNTS "<<pschedules<<' '<<presources<<' '<<pinstruments<<' '<<pvalid<<' '<<pft<<endl;
}
