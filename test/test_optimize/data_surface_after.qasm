OPENQASM 2.0;
include "qelib1.inc";
qreg q[4];
creg c[4];
x q[3];
ry(-pi/2) q[0];
cz q[2],q[0];
ry(pi/2) q[0];
ry(-pi/2) q[1];
z q[1];
x q[1];
ry(-pi/2) q[2];
cz q[0],q[2];
ry(pi/2) q[2];
ry(-pi/2) q[0];
cz q[2],q[0];
ry(pi/2) q[0];
ry(-pi/2) q[3];
cz q[0],q[3];
ry(pi/2) q[3];
ry(-pi/2) q[1];
cz q[3],q[1];
ry(pi/2) q[1];
ry(-pi/2) q[0];
cz q[2],q[0];
ry(pi/2) q[0];
ry(-pi/2) q[2];
cz q[1],q[2];
ry(pi/2) q[2];
ry(pi/2) q[1];
cz q[3],q[1];
ry(-pi/2) q[1];
ry(pi/2) q[1];
cz q[2],q[1];
ry(-pi/2) q[1];
x q[3];
x q[1];
ry(pi/2) q[3];
cz q[2],q[3];
ry(-pi/2) q[3];
ry(pi/2) q[3];
cz q[1],q[3];
ry(-pi/2) q[3];
ry(-pi/2) q[0];
cz q[3],q[0];
ry(pi/2) q[0];
ry(-pi/2) q[1];
z q[1];
rz(0.3) q[1];
ry(-pi/2) q[1];
z q[1];
z q[1];
ry(-pi/2) q[1];
ry(pi/2) q[3];
cz q[1],q[3];
ry(-pi/2) q[3];
z q[1];
ry(-pi/2) q[1];
ry(pi/2) q[1];
cz q[0],q[1];
ry(-pi/2) q[1];
x q[1];
ry(pi/2) q[3];
cz q[2],q[3];
ry(-pi/2) q[3];
ry(pi/2) q[3];
cz q[1],q[3];
ry(-pi/2) q[3];
x q[1];
ry(pi/2) q[3];
cz q[1],q[3];
ry(-pi/2) q[3];
ry(pi/2) q[3];
cz q[0],q[3];
ry(-pi/2) q[3];
ry(-pi/2) q[2];
z q[2];
rz(0.6) q[2];
ry(-pi/2) q[2];
z q[2];
ry(-pi/2) q[1];
cz q[0],q[1];
ry(pi/2) q[1];
ry(-pi/2) q[1];
z q[1];
x q[1];
ry(pi/2) q[3];
cz q[2],q[3];
ry(-pi/2) q[3];
ry(pi/2) q[3];
cz q[1],q[3];
ry(-pi/2) q[3];
ry(-pi/2) q[0];
cz q[3],q[0];
ry(pi/2) q[0];
x q[1];
ry(-pi/2) q[1];
cz q[3],q[1];
ry(pi/2) q[1];
x q[1];
ry(-pi/2) q[3];
cz q[0],q[3];
ry(pi/2) q[3];
x q[1];
ry(-pi/2) q[3];
cz q[0],q[3];
ry(pi/2) q[3];
ry(-pi/2) q[0];
cz q[3],q[0];
ry(pi/2) q[0];
ry(-pi/2) q[3];
cz q[1],q[3];
ry(pi/2) q[3];
ry(-pi/2) q[1];
z q[1];
