//Audification
(
SynthDef(\audification, {
	arg amp=1,freq=200,pan=0,out=0, numharm=1, lg=0.05;
	var signal;
	signal= Blip.ar(mul:amp,freq:freq, numharm: numharm);
	// Offset.ar(out, Pan2.ar(signal, pan.lag(lg), amp.lag(lg)));
	// signal=Pan2.ar(signal * amp, pan);
	OffsetOut.ar(out,signal!2);
}).add;
);
Synth.new(\audification,[\freq,200, \amp, 0.3])
//R peaks drops
(
~bfrdrops = Buffer.readChannel(s,"/Users/lorenaaldana/Dropbox/PhD/PhD Sonification/ECG Sonification/2016/MonitoringSounds/Drop_Main.wav" ,bufnum:10);
);
(
SynthDef(\rpeaks_drops, {
	arg amp=1,out=0, rate=1, envc=50, bufnum=10, pan=0,startpos=0, doneA=2,t_trig=1,buf;
	var signal, env;
	signal = PlayBuf.ar(2, bufnum, BufRateScale.kr(bufnum)); //or 2 if stereo
	//signal = PlayBuf.ar(2,buf, rate: BufRateScale.kr(buf) * rate, trigger:t_trig, startPos:startpos, doneAction:doneA);
	env= EnvGen.kr(Env.perc(0.02, (~bfrdrops.duration-0.05), 1, curve:envc), doneAction:2);
	// signal=(signal * env * amp);
	signal=Pan2.ar(signal * env* amp, pan);
	OffsetOut.ar(out,signal);
}).send(s);
);
~bfrdrops.play;
Synth.new(\rpeaks_drops,[\rate,10])
Synth.new(\rpeaks_drops,[\buf, ~bfrdrops.bufnum, \rate,0.midiratio, \startpos, 1200]);


//HRV
(
SynthDef(\hrvar, {
	arg amp=1,freq=200,pan=0,out=0, numharm=1;
	var signal;
	signal= Blip.ar(mul:amp,freq:freq, numharm: numharm)*
		EnvGen.kr(Env.perc(attackTime: 0.01, releaseTime: 0.1, level: 01, curve: -4), doneAction:2);
	// signal=Pan2.ar(signal * amp, pan);
	OffsetOut.ar(out,signal!2);
}).add;
);
Synth.new("hrvar", [\freq, 800])



//AML
(
SynthDef(\AML, {
	arg amp=1,freq=200,pan=0,out=0, numharm=2;
	var signal;
	signal= Blip.ar(mul:amp,freq:freq, numharm: numharm)*
		EnvGen.kr(Env.perc(attackTime: 0.01, releaseTime: 0.2, level: 01, curve: -4), doneAction:2);
	OffsetOut.ar(out,signal!2);
}).add;
);
Synth.new("AML", [\freq, 400, \numharm, 2])

//To Stop
(
SynthDef(\stop, {
	arg amp=1,freq=200,pan=0,out=0, numharm=2;
	var signal;
	s.freeAll;
	["algo"].postln
}).add;
);
Synth.new("stop", [\freq, 1])


// OSC to Stop All Synths from 'Stop Sonification button'
(
~oscreceiveSTOP = OSCresponderNode(nil, '/StopSynths', {
	arg time, responder, msg;
    [msg].postln;
	s.freeAll;
}).add;
)
~oscreceiveSTOP.remove;


//// to record
s.boot;
ServerOptions.outDevices
Server.default.options.outDevice_("JackRouter")
s.reboot;