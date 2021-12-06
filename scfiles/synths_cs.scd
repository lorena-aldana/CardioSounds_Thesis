// Marimba synth

(

var cur_dir = thisProcess.nowExecutingPath.dirname +/+ "/sounds/";

h = Buffer.readChannel(s, cur_dir +/+ "C MEDIUM.wav",channels:[0], bufnum:5);
j = Buffer.readChannel(s, cur_dir +/+ "E MEDIUM.wav" ,channels:[0], bufnum:6);
k = Buffer.readChannel(s, cur_dir +/+  "G MEDIUM.wav",channels:[0], bufnum:7);


SynthDef.new(\marimba, {
	arg amp=0.5, out=0, rate=1.0, buf, numtriggers=10, graindur= 0.3, envdur=0.5, startpos=0.0;
	var signal, winenv;

	winenv = Env([0, 0.7, 0.9, 0.2, 0], [0.01, 0.02, 0.3, 0.05], [-2, -2, 4, -2]);
	//winenv = Env([0, 0.8, 1, 0.2, 0], [0.01, 0.02, 0.3, 0.05], curve: 'sin');*/
	z = Buffer.sendCollection(s, winenv.discretize, 1);
	// ~winenv = Env([0, 0.8, 1, 0.2, 0], [0.01, 0.02, 0.2, 0.05], [-2, -2, 4, -2]);
	signal = GrainBuf.ar(1,Impulse.kr(numtriggers), graindur, buf, rate: BufRateScale.kr(buf) *rate, pos:startpos, envbufnum:z, maxGrains:50);
	signal=signal*amp*EnvGen.kr(Env.perc(attackTime: 0.2, releaseTime: envdur, level: 1, curve: -8), doneAction:2);

	Out.ar(out,signal!2);
}).add;
)

Synth.new(\marimba,[\buf, 5])

Synth.new(\marimba,[\buf, 5, \rate, 1, \startpos, 0.0, \envdur, 1.0, \graindur, 0.3, \numtriggers, 1, \amp, 0.7]);


// Basic synth
(
SynthDef("basic_synth", {|freq=400, dur=0.4, att=0.01, amp=0.3, num=4, pan=0| Out.ar( 0, Pan2.ar(Blip.ar(freq, num)* EnvGen.kr(Env.perc(att, dur, 1, -2), doneAction: 2), pan, amp)) }).send(s)
)
Synth.new(\basic_synth)


//ECGrains

(
SynthDef(\grain_sin_test, {
	arg amp = 0.5, envdur=0.4, graindur= 0.1, freq=100, numtriggers=10;
    var grains, signal;

	grains= GrainSin.ar(2, Impulse.kr(numtriggers), graindur, freq, envbufnum:-1, maxGrains:500);
	signal= grains*amp*EnvGen.kr(Env.perc(attackTime: 0.2, releaseTime: envdur, level: 1, curve: -8), doneAction:2);
	Out.ar(0, signal);
    }).add;
)

Synth.new(\grain_sin_test, [ \amp, 0.1, \envdur, 1.0, \graindur, 0.04, \freq, 400,  \numtriggers, [321]])
