OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[24];
// STAGE encoder
reset q[0];
reset q[1];
reset q[2];
reset q[3];
reset q[4];
reset q[5];
reset q[6];
h q[6];
reset q[7];
reset q[8];
h q[8];
reset q[9];
reset q[10];
h q[10];
reset q[11];
reset q[12];
h q[12];
reset q[13];
h q[13];
reset q[14];
cx q[6],q[3];
cx q[10],q[11];
cx q[6],q[1];
cx q[10],q[9];
cx q[12],q[11];
cx q[13],q[6];
cx q[13],q[10];
cx q[12],q[7];
cx q[3],q[2];
cx q[13],q[7];
cx q[7],q[0];
cx q[11],q[14];
cx q[8],q[7];
cx q[10],q[14];
cx q[13],q[5];
cx q[8],q[1];
cx q[10],q[3];
cx q[6],q[5];
cx q[8],q[9];
cx q[1],q[0];
cx q[11],q[4];
cx q[5],q[4];
cx q[9],q[14];
cx q[9],q[2];
cx q[12],q[5];
// STAGE TA
reset q[15];
reset q[16];
reset q[17];
reset q[18];
h q[18];
cx q[8],q[15];
cx q[18],q[15];
cx q[15],q[17];
cx q[7],q[15];
cx q[15],q[16];
cx q[9],q[15];
cx q[14],q[15];
cx q[12],q[16];
cx q[13],q[16];
cx q[9],q[17];
cx q[10],q[17];
cx q[13],q[17];
cx q[18],q[15];
cx q[18],q[16];
cx q[18],q[17];
measure q[15] -> c[1];
measure q[16] -> c[2];
measure q[17] -> c[3];
h q[18];
measure q[18] -> c[4];
// STAGE TB
reset q[19];
reset q[20];
reset q[21];
reset q[22];
h q[22];
cx q[6],q[19];
cx q[22],q[19];
cx q[19],q[21];
cx q[1],q[19];
cx q[19],q[20];
cx q[5],q[19];
cx q[0],q[19];
cx q[2],q[20];
cx q[3],q[20];
cx q[5],q[21];
cx q[4],q[21];
cx q[3],q[21];
cx q[22],q[19];
cx q[22],q[20];
cx q[22],q[21];
measure q[19] -> c[5];
measure q[20] -> c[6];
measure q[21] -> c[7];
h q[22];
measure q[22] -> c[8];
// STAGE PA
reset q[23];
reset q[24];
reset q[25];
h q[25];
cx q[3],q[23];
cx q[25],q[23];
cx q[10],q[23];
cx q[23],q[24];
cx q[4],q[23];
cx q[11],q[23];
cx q[6],q[24];
cx q[13],q[24];
cx q[25],q[23];
cx q[25],q[24];
measure q[23] -> c[9];
measure q[24] -> c[10];
h q[25];
measure q[25] -> c[11];
// STAGE PB
reset q[26];
reset q[27];
reset q[28];
h q[28];
cx q[6],q[26];
cx q[28],q[26];
cx q[13],q[26];
cx q[26],q[27];
cx q[5],q[26];
cx q[12],q[26];
cx q[1],q[27];
cx q[8],q[27];
cx q[28],q[26];
cx q[28],q[27];
measure q[26] -> c[12];
measure q[27] -> c[13];
h q[28];
measure q[28] -> c[14];
// STAGE late_logical_X_verifier
reset q[30];
reset q[29];
h q[29];
cx q[29],q[1];
cx q[29],q[30];
cx q[29],q[3];
cx q[29],q[5];
cx q[29],q[7];
cx q[29],q[9];
cx q[29],q[11];
cx q[29],q[30];
cx q[29],q[13];
h q[29];
measure q[29] -> c[0];
measure q[30] -> c[23];
// STAGE transversal_T
t q[0];
tdg q[1];
t q[2];
tdg q[3];
t q[4];
tdg q[5];
t q[6];
tdg q[7];
t q[8];
tdg q[9];
t q[10];
tdg q[11];
t q[12];
tdg q[13];
t q[14];
// STAGE coherent_gauge_frame
cx q[0],q[7];
cx q[1],q[8];
cx q[2],q[9];
cx q[3],q[10];
cx q[4],q[11];
cx q[5],q[12];
cx q[6],q[13];
// STAGE bulk_readout
h q[7];
measure q[7] -> c[15];
h q[8];
measure q[8] -> c[16];
h q[9];
measure q[9] -> c[17];
h q[10];
measure q[10] -> c[18];
h q[11];
measure q[11] -> c[19];
h q[12];
measure q[12] -> c[20];
h q[13];
measure q[13] -> c[21];
h q[14];
measure q[14] -> c[22];
// DETECTOR c[0]
// DETECTOR c[1]
// DETECTOR c[2]
// DETECTOR c[3]
// DETECTOR c[4]
// DETECTOR c[5]
// DETECTOR c[6]
// DETECTOR c[7]
// DETECTOR c[8]
// DETECTOR c[9]
// DETECTOR c[10]
// DETECTOR c[11]
// DETECTOR c[12]
// DETECTOR c[13]
// DETECTOR c[14]
// DETECTOR c[15] c[16] c[17] c[18] c[19] c[20] c[21] c[22]
// DETECTOR c[23]
// FRAME_X(0)
// FRAME_Z(0) c[15] c[16] c[17] c[18] c[19] c[20] c[21]
