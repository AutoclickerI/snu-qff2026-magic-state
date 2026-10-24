OPENQASM 2.0;
include "qelib1.inc";
qreg q[36];
creg c[24];
// STAGE rm15_encoder
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
// STAGE rm15_logical_X_verifier
reset q[15];
h q[15];
cx q[15],q[1];
cx q[15],q[3];
cx q[15],q[5];
cx q[15],q[7];
cx q[15],q[9];
cx q[15],q[11];
cx q[15],q[13];
h q[15];
measure q[15] -> c[0];
// STAGE TB
reset q[15];
reset q[16];
reset q[17];
reset q[18];
h q[18];
cx q[6],q[15];
cx q[18],q[15];
cx q[15],q[17];
cx q[1],q[15];
cx q[15],q[16];
cx q[5],q[15];
cx q[0],q[15];
cx q[2],q[16];
cx q[3],q[16];
cx q[5],q[17];
cx q[4],q[17];
cx q[3],q[17];
cx q[18],q[15];
cx q[18],q[16];
cx q[18],q[17];
measure q[15] -> c[1];
measure q[16] -> c[2];
measure q[17] -> c[3];
h q[18];
measure q[18] -> c[4];
// STAGE PB
reset q[15];
reset q[16];
reset q[18];
h q[18];
cx q[6],q[15];
cx q[18],q[15];
cx q[13],q[15];
cx q[15],q[16];
cx q[5],q[15];
cx q[12],q[15];
cx q[1],q[16];
cx q[8],q[16];
cx q[18],q[15];
cx q[18],q[16];
measure q[15] -> c[5];
measure q[16] -> c[6];
h q[18];
measure q[18] -> c[7];
// STAGE transversal_T
barrier q[0],q[1],q[2],q[3],q[4],q[5],q[6],q[7],q[8],q[9],q[10],q[11],q[12],q[13],q[14],q[15],q[16],q[17],q[18],q[19],q[20],q[21],q[22],q[23],q[24],q[25],q[26],q[27],q[28],q[29],q[30],q[31],q[32],q[33],q[34],q[35];
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
// STAGE steane_zero_encoder
reset q[19];
h q[19];
reset q[20];
reset q[21];
h q[21];
reset q[22];
reset q[23];
h q[23];
reset q[24];
reset q[25];
reset q[15];
cx q[21],q[22];
cx q[21],q[20];
cx q[23],q[22];
cx q[19],q[20];
cx q[23],q[24];
cx q[20],q[25];
cx q[23],q[25];
cx q[19],q[24];
cx q[21],q[15];
cx q[25],q[15];
cx q[24],q[15];
measure q[15] -> c[8];
// STAGE transversal_rm_to_steane
cx q[0],q[19];
cx q[1],q[20];
cx q[2],q[21];
cx q[3],q[22];
cx q[4],q[23];
cx q[5],q[24];
cx q[6],q[25];
// STAGE rm15_X_measurement
h q[0];
measure q[0] -> c[9];
h q[1];
measure q[1] -> c[10];
h q[2];
measure q[2] -> c[11];
h q[3];
measure q[3] -> c[12];
h q[4];
measure q[4] -> c[13];
h q[5];
measure q[5] -> c[14];
h q[6];
measure q[6] -> c[15];
h q[7];
measure q[7] -> c[16];
h q[8];
measure q[8] -> c[17];
h q[9];
measure q[9] -> c[18];
h q[10];
measure q[10] -> c[19];
h q[11];
measure q[11] -> c[20];
h q[12];
measure q[12] -> c[21];
h q[13];
measure q[13] -> c[22];
h q[14];
measure q[14] -> c[23];
// DETECTOR c[0]
// DETECTOR c[1]
// DETECTOR c[2]
// DETECTOR c[3]
// DETECTOR c[4]
// DETECTOR c[5]
// DETECTOR c[6]
// DETECTOR c[7]
// DETECTOR c[8]
// DETECTOR c[9] c[10] c[14] c[15] c[16] c[17] c[21] c[22]
// DETECTOR c[12] c[13] c[14] c[15] c[19] c[20] c[21] c[22]
// DETECTOR c[10] c[11] c[12] c[15] c[17] c[18] c[19] c[22]
// DETECTOR c[16] c[17] c[18] c[19] c[20] c[21] c[22] c[23]
// FRAME_X(0)
// FRAME_Z(0) c[9] c[10] c[11] c[12] c[13] c[14] c[15]
