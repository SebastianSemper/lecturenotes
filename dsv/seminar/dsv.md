------------------------------------
# digitale signalverarbeitung uebung
------------------------------------



## 13/02 konsultation 



## 04/02
->  see notebook `sinc-dirichlet`
-   sinc interpol
-   CT signal, aperiodic, BB -> implicit rect im spectrum -> sinc faltung signal
-   sinc error, 1/x einhuellende
-   was wenn wir periodic haben?
-   periodify sinc -> abtastung rect -> sum complex harmonics (dirichlet)
-   N even / N odd thoughts
-   implementation sinc interpol -> error outside und inside
-   failed implementation with dirichlet :D
-   notebook has scipy.special.diric kernel (but also fails for even ones)
-   later laborfuehrung



## 28/01
-   VL ueber splines
    -   splines
        -   polynome, expansion als conv
        -   B splines durch mehrfache rect conv
        -   DOF und properties an den nodes (bzw fuer die segments)
        -   brauche ich fuer die analytische spline ableitung mehr speicherplatz als
            wie fuer nur die evaluation ?
    -   spline interpolation
        -   warum coeff nicht signal?
        -   coeffizienten die interpolatieren durch digitales filtern
        -   bspline samplen, IIR, z trafo -> implementation
        -   randbedingungen
    -   splines vs sincs
        -   interpolationskernel versus evaluation
        -   gegen inf == sinc

-   heute uebung
-   spline evaluation / implementation auf gpu (heute mehr dazu und code gucken)
-   prefilter implementation
    -   IIR ueber diff equation
    -   boundary ausrechnen
    -   aufteilen in a und ac
    -   computational complexity
-   evaluation implementation
    -   weights durch segments polynome
    -   nur finite coeffs
    -   wie sieht hier 2D aus?
-   jacobian implementation
    -   deriv of expansion -> different but similar kernel, same coeffs
-   in reality
    -   computational complexity
    -   refomulation as linear -> can use hardware
    -   memory models / high performance computing thoughts



## 21/01
-   story audio signal filter live concert
-   signel brosessing issues
    -   basics: sampling $x(t)->x[n]$, whats with $X(f)->$
    -   x aperiodic: filtering = linear convolution
    -   FFT is efficient implementation of circular convolution
    -   also: time domain aliasing

-   naive: just periodify x and use our beloved DFT
    -   real life issues: very long time signal
    -   listen to "live" concert after sampling and filtering complete x

-   x long, but h is short ?
    -   how to make it (nearly) live -> lets block it
    -   (now smaller) linear convs ?
    -   some stuff is outside our blocks
    -   put stuff into the next block
    -   implementation somehow with fft to be faster ?

-   difference linear vs circular convolution
    -   how can we fake linear conv to use FFT
    -   DFT tooling assumes periodic -> periodify but how ?
    -   damn aliasing. lets zeropad

-   implementation FIR
    -   circular conv as fft -> nice
    -   linear conv complexity ... long signal ... ?
    -   somehow use fft for linear conv would be nice
    -   how to avoid error of circular vs linear ?
    -   zp sizes dependend on h, fft size then ?
    -   what about h vs x size fft size?

-   implementation IIR
    -   iir implementation ?



## 14/01
-   fft continued, alg complexity, butterfly pattern

## 7/01
-   zeropadding / resolution
-   fft beginnings



## 10/12
-   VL mit z trafo eigenschaften durch
    -   z trafo eingefuehrt, aber noch nicht als system sonder nur signal style
    -   einfache z trafos und inverse davon ueben

-   last time frage: ist decomposition unique? wie wuerde man den beweis fuehren
    -> seb meint, lass mal gucken was bei der annahme non unique passiert
    


## 3/12
-   VL 3.3 zuende
    -   einfach proakis uebungen / examples durchballern
    -   impulsantworten, was passiert, was kann man "lesen"
-   frage: moivre gerade ungerade connection?



## 26/11
-> obsidian
-   VL: codesnippet 10 fertig (3.3.1)



## 19/11
-   keine VL weil krank
-   mandelbrot



## 12/11
-   sinc interpolation: snippet
    -   warum falsch
        -   randbedingung: dirichlet kernel
        -   abfall 1/x accuracy
    -   computational aspect


## 05/11
-   ghyrrosbuch lesen zu sampling theorem
    -   ghyrrosbuch seiten fehlend
-   MIT OCW mal abchecken (maybe direkt nur zu sampling theorem)
    -> gut das war nen useless nerdsnipe bei den videos
    -> die sachen auf der homepage sind super als takehome messages
    -> es gibt DSP und Signals & Systems als courses
-   codesnippet mal tryen
-   mit ocw sigsys 2011, lecture 16, minute 15



## seb notes
-   item beispiel 2.3.6./2.3.7 fuer stabilitaet
-   Zu kapitel 3.1 im Skript: Ubung: Problem 2.1, 2.2 in Python, 2.3 ausm ghyrrosbuch
-   beispiele: \cite[ex. 2.2.1]{proakis2013} (a-c vorlesung, rest uebung)
-   blockschaltbilder: adder, multiplikator, scaler, delay, uebung \cite[ex 2.2.3]{proakis2013}(per hand, per modularem code)
-   sinc -> dirichlet kernel
-   exerzieren von beispiel 2.3.2, uebung programmieren (naiv summieren, scipy convolve)
-   exerzieren von beispiel 2.3.3, uebung programmieren der approximation 


## laters
- MIT OCW take home notes (maybe direkt ins gitlab dsv reinballern)
-   clipgrab MIT OCW signel brosesing
-   marc dsp illustations fuer z trafo?
-   nochmal genauer die FIR IIR lorenz discussion hoch holen und mit z trafo was
    ich gelern hab angucken / cauchy integral theorem ?  lorenz meinte FIR kann
    nur wenn z trafo polstellen in der null hat ...

