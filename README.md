
	🧩 (A) COMPORTAMENTE CALCULATE FRAME CU FRAME
Bazate pe geometrie instantanee și poziții relative.
Acestea se pot detecta doar analizând coordonatele dintr-un singur frame, fără istoric temporal.
Contact (între indivizi)	verifică atingerea între corpuri	body₁, body₂	distanța body₁–body₂
Nose-to-nose sniffing	nas–nas apropiat	nose₁, nose₂	dist(nose₁, nose₂)
Nose-to-tail sniffing	nas₁ aproape de coada₂	nose₁, tail_base₂	dist(nose₁, tail₂)
Facing / orientation toward	un șoarece orientat spre altul	nose₁, body₁, body₂	unghi între orientare și vectorul inter-corp

	🧮 (B) COMPORTAMENTE CALCULATE PE FERESTRE TEMPORALE (Δt)
Bazate pe variații în timp — mișcare, viteze, unghiuri, distanțe.
Aici analizezi secvențe de câteva zeci de frame-uri (0.5–2 secunde), pentru a detecta tendințe.
Locomotion / walking	mișcare constantă a corpului	body_center	viteză (Δx, Δy/Δt)
Running / fast locomotion	versiune rapidă a mișcării	body_center	viteză > prag
Rearing (ridicare)	cap ridicat, distanță mică nas–corp, mișcare verticală	nose, body_center	variație rapidă dist(nose, body) + stabilitate spațială
Grooming (curățare)	mișcări oscilante rapide ale nasului spre corp	nose, body_center	dist(nose, body) mică + variație rapidă
Sniffing (exploration)	mișcări rapide ale nasului, fără deplasare mare	nose, body_center	mică deplasare totală + variații mici de unghi
Turning / rotation	rotire a corpului fără deplasare mare	nose, body_center	Δ unghi(nose–body) mare, viteză mică
Freezing (înghețare)	aproape fără mișcare în Δt	body_center	viteză ≈ 0
Approach	distanța body₁–body₂ scade în Δt	body₁, body₂	Δ dist < 0
Avoidance	distanța body₁–body₂ crește rapid	body₁, body₂	Δ dist > 0
Following	direcția de mișcare a unui șoarece spre celălalt + dist mică	body₁, body₂	orientare + Δ dist
Chasing	viteze mari + apropiere constantă	body₁, body₂	speed₁ mare + Δ dist < 0