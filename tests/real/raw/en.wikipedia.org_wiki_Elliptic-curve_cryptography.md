---
title: Elliptic-curve cryptography - Wikipedia
source: "https://en.wikipedia.org/wiki/Elliptic-curve_cryptography"
canonical_url: "https://en.wikipedia.org/wiki/Elliptic-curve_cryptography"
language: en
domdown_version: 0.3.4
image: "https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Wiki_letter_w_cropped.svg/20px-Wiki_letter_w_cropped.svg.png"
---
**Elliptic-curve cryptography** (**ECC**) is an approach to [public-key cryptography](https://en.wikipedia.org/wiki/Public-key_cryptography) based on the [algebraic structure](https://en.wikipedia.org/wiki/Algebraic_structure) of [elliptic curves](https://en.wikipedia.org/wiki/Elliptic_curve) over [finite fields](https://en.wikipedia.org/wiki/Finite_field). ECC allows smaller keys to provide equivalent security, compared to cryptosystems based on modular exponentiation in [finite fields](https://en.wikipedia.org/wiki/Finite_field), such as the [RSA cryptosystem](https://en.wikipedia.org/wiki/RSA_cryptosystem) and [ElGamal cryptosystem](https://en.wikipedia.org/wiki/ElGamal_encryption).[[ 1 ]](#cite_note-:0-1)

Elliptic curves are applicable for [key agreement](https://en.wikipedia.org/wiki/Key_agreement), [digital signatures](https://en.wikipedia.org/wiki/Digital_signature), [pseudo-random generators](https://en.wikipedia.org/wiki/Cryptographically_secure_pseudorandom_number_generator) and other tasks. Indirectly, they can be used for [encryption](https://en.wikipedia.org/wiki/Encryption) by combining the key agreement with a [symmetric encryption](https://en.wikipedia.org/wiki/Symmetric-key_algorithm) scheme. They are also used in several [integer factorization](https://en.wikipedia.org/wiki/Integer_factorization) [algorithms](https://en.wikipedia.org/wiki/Algorithm) that have applications in cryptography, such as [Lenstra elliptic-curve factorization](https://en.wikipedia.org/wiki/Lenstra_elliptic-curve_factorization).

## History

| [![[icon]](https://upload.wikimedia.org/wikipedia/commons/thumb/1/1c/Wiki_letter_w_cropped.svg/40px-Wiki_letter_w_cropped.svg.png)](https://en.wikipedia.org/wiki/File:Wiki_letter_w_cropped.svg) | This section **needs expansion** with: a global view that expands coverage to include non-U.S. standards and standards bodies. You can help by [adding missing information](https://en.wikipedia.org/w/index.php?title=Elliptic-curve_cryptography&action=edit§ion=). |
| --- | --- |

The use of elliptic curves in cryptography was suggested independently by [Neal Koblitz](https://en.wikipedia.org/wiki/Neal_Koblitz)[[ 2 ]](#cite_note-2) and [Victor S. Miller](https://en.wikipedia.org/wiki/Victor_S._Miller)[[ 3 ]](#cite_note-3) in 1985. Elliptic curve cryptography algorithms entered wide use starting in 2004.

At the [RSA Conference](https://en.wikipedia.org/wiki/RSA_Conference) 2005, the [National Security Agency](https://en.wikipedia.org/wiki/National_Security_Agency) (NSA) announced [Suite B](https://en.wikipedia.org/wiki/NSA_Suite_B), which used ECC for digital signature generation and key exchange.[[ 1 ]](#cite_note-:0-1) Suite B was later superseded by the Commercial National Security Algorithm Suite (CNSA), and NSA announced CNSA 2.0 as a quantum-resistant transition suite for national security systems.[[ 7 ]](#cite_note-nsa-cnsa2-7)

Since the early 2000s, cryptographic primitives based on bilinear mappings on various elliptic curve groups, such as the [Weil](https://en.wikipedia.org/wiki/Weil_pairing) and [Tate pairings](https://en.wikipedia.org/wiki/Tate_pairing), have been studied. Schemes based on these primitives include [identity-based encryption](https://en.wikipedia.org/wiki/Identity-based_encryption) as well as pairing-based signatures, [signcryption](https://en.wikipedia.org/wiki/Signcryption), [key agreement](https://en.wikipedia.org/wiki/Key_agreement), and [proxy re-encryption](https://en.wikipedia.org/wiki/Proxy_re-encryption).[[ 8 ]](#cite_note-8)

Elliptic curve cryptography is used successfully in numerous popular protocols, such as [Transport Layer Security](https://en.wikipedia.org/wiki/Transport_Layer_Security) and [Bitcoin](https://en.wikipedia.org/wiki/Bitcoin).

### Security concerns

Additionally, in August 2015, the NSA announced that it planned to replace Suite B with a new cipher suite due to concerns about [quantum computing](https://en.wikipedia.org/wiki/Quantum_computing) attacks on ECC.[[ 13 ]](#cite_note-nsaquantum-13)[[ 14 ]](#cite_note-nsaQCfaq-14) NSA later published CNSA 2.0 guidance for a transition to quantum-resistant algorithms for national security systems.[[ 7 ]](#cite_note-nsa-cnsa2-7)

### Patents

While the RSA patent expired in 2000, there may be patents in force covering certain aspects of ECC technology, including at least one ECC scheme ([ECMQV](https://en.wikipedia.org/wiki/ECMQV)). However, [RSA Laboratories](https://en.wikipedia.org/wiki/RSA_Security)[[ 15 ]](#cite_note-15) and [Daniel J. Bernstein](https://en.wikipedia.org/wiki/Daniel_J._Bernstein)[[ 16 ]](#cite_note-16) have argued that the [US government](https://en.wikipedia.org/wiki/Federal_government_of_the_United_States) elliptic curve digital signature standard (ECDSA; NIST FIPS 186-3) and certain practical ECC-based key exchange schemes (including ECDH) can be implemented without infringing those patents.

## Elliptic curve theory

For the purposes of this article, an _elliptic curve_ is a [plane curve](https://en.wikipedia.org/wiki/Plane_curve) over a [finite field](https://en.wikipedia.org/wiki/Finite_field) (rather than the real numbers). A common form for curves over finite fields of [characteristic](https://en.wikipedia.org/wiki/Characteristic_(algebra)#Case_of_fields) not equal to 2 or 3 consists of the points satisfying the equation

y

2

=

x

3

+

a

x

+

b

,

{\displaystyle y^{2}=x^{3}+ax+b,}

![{\displaystyle y^{2}=x^{3}+ax+b,}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a7f42f12ff83c4b3f5a7afb4043d2fe29545ebdb)

along with a distinguished [point at infinity](https://en.wikipedia.org/wiki/Point_at_infinity), denoted ∞. Curves over fields of characteristic 2 or 3, and curves used in other representations such as Montgomery or Edwards form, are written differently.

This set of points, together with the [group operation of elliptic curves](https://en.wikipedia.org/wiki/Elliptic_curve#Group_law), is an [abelian group](https://en.wikipedia.org/wiki/Abelian_group), with the point at infinity as an identity element. The structure of the group is inherited from the [divisor group](https://en.wikipedia.org/wiki/Divisor_(algebraic_geometry)) of the underlying [algebraic variety](https://en.wikipedia.org/wiki/Algebraic_variety):

Div

0

⁡

(

E

)

→

Pic

0

⁡

(

E

)

≃

E

.

{\displaystyle \operatorname {Div} ^{0}(E)\to \operatorname {Pic} ^{0}(E)\simeq E.}

![{\displaystyle \operatorname {Div} ^{0}(E)\to \operatorname {Pic} ^{0}(E)\simeq E.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b6e027e62000efd35166777b2ba01e686053fcf5)

### Application to cryptography

[Public-key cryptography](https://en.wikipedia.org/wiki/Public-key_cryptography) is based on the [intractability](https://en.wikipedia.org/wiki/Intractability_(complexity)#Intractability) of certain mathematical [problems](https://en.wikipedia.org/wiki/Computational_hardness_assumption). Early public-key systems, such as [RSA](https://en.wikipedia.org/wiki/RSA_(cryptosystem))'s 1983 patent, based their security on the assumption that it is difficult to [factor](https://en.wikipedia.org/wiki/Integer_factorization) a large integer composed of two or more large prime factors which are far apart. For elliptic-curve protocols, a central hardness assumption is the [elliptic curve discrete logarithm problem](https://en.wikipedia.org/wiki/Elliptic_curve_discrete_logarithm_problem) (ECDLP): given a public base point P {\displaystyle P}![{\displaystyle P}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b4dc73bf40314945ff376bd363916a738548d40a) and another point Q = k P {\displaystyle Q=kP}![{\displaystyle Q=kP}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a743b633091c7b4f332e9f5eaaeff88772821a8e), it should be infeasible to recover k {\displaystyle k}![{\displaystyle k}](https://wikimedia.org/api/rest_v1/media/math/render/svg/c3c9a2c7b599b37105512c5d570edc034056dd40). Key-agreement protocols such as ECDH rely on related Diffie–Hellman assumptions, such as the difficulty of computing a b P {\displaystyle abP}![{\displaystyle abP}](https://wikimedia.org/api/rest_v1/media/math/render/svg/977b645c83d2c1768ba65b358be77243713586c1) from P {\displaystyle P}![{\displaystyle P}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b4dc73bf40314945ff376bd363916a738548d40a), a P {\displaystyle aP}![{\displaystyle aP}](https://wikimedia.org/api/rest_v1/media/math/render/svg/b3dbc421219b2a77d7810c7030f549647a3f4571), and b P {\displaystyle bP}![{\displaystyle bP}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f9c826d7764e8887d8d69d9c30b6bf9e0a4cf931). The security of elliptic curve cryptography depends on the ability to compute [point multiplication](https://en.wikipedia.org/wiki/Elliptic_curve_point_multiplication) efficiently and the apparent inability to reverse it for properly chosen curves and key sizes. The size and structure of the curve group, rather than only the total number of coordinate pairs satisfying the curve equation, determine the difficulty of the problem.

The primary benefit promised by elliptic curve cryptography over alternatives such as RSA is a smaller [key size](https://en.wikipedia.org/wiki/Key_size), reducing storage and transmission requirements.[[ 1 ]](#cite_note-:0-1) For example, a 256-bit elliptic curve public key should provide [comparable security](https://en.wikipedia.org/wiki/Security_level) to a 3072-bit RSA public key.

### Cryptographic schemes

Several [discrete logarithm](https://en.wikipedia.org/wiki/Discrete_logarithm)-based protocols have been adapted to elliptic curves, replacing the group ( Z p ) × {\displaystyle (\mathbb {Z} _{p})^{\times }}![{\displaystyle (\mathbb {Z} _{p})^{\times }}](https://wikimedia.org/api/rest_v1/media/math/render/svg/330c9efd1ac7f717428e734aa2ed3dcf97e47756) with an elliptic-curve group:

## Implementation

Some common implementation considerations include:

### Domain parameters

To use ECC, all parties must agree on all the elements defining the elliptic curve, that is, the _domain parameters_ of the scheme. The underlying finite field is typically either a prime field, denoted F p {\displaystyle \mathbb {F} _{p}}![{\displaystyle \mathbb {F} _{p}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2d35035371db7bee93733c68c1802114c17d8bb4), or a binary field, denoted F 2 m {\displaystyle \mathbb {F} _{2^{m}}}![{\displaystyle \mathbb {F} _{2^{m}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/950de5de23e6ba61c1a5186dae752ae92ff4870e). In the binary case, m {\displaystyle m}![{\displaystyle m}](https://wikimedia.org/api/rest_v1/media/math/render/svg/0a07d98bb302f3856cbabc47b2b9016692e3f7bc) and an irreducible reduction polynomial f {\displaystyle f}![{\displaystyle f}](https://wikimedia.org/api/rest_v1/media/math/render/svg/132e57acb643253e7810ee9702d9581f159a1c61) specify the field representation; f {\displaystyle f}![{\displaystyle f}](https://wikimedia.org/api/rest_v1/media/math/render/svg/132e57acb643253e7810ee9702d9581f159a1c61) is not an auxiliary curve. The elliptic curve is defined by the coefficients in its defining equation. Finally, the cyclic subgroup is defined by its [generator](https://en.wikipedia.org/wiki/Generating_set_of_a_group) (a.k.a. _base point_) _G_. For cryptographic application, the [order](https://en.wikipedia.org/wiki/Order_(group_theory)) of _G_, that is the smallest positive number _n_ such that n G = O {\displaystyle nG={\mathcal {O}}}![{\displaystyle nG={\mathcal {O}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/69301d032dc873e947b4ff794ca3af6b42c45f66) (the [point at infinity](https://en.wikipedia.org/wiki/Point_at_infinity) of the curve, and the [identity element](https://en.wikipedia.org/wiki/Identity_element)), is normally prime. Since _n_ is the size of a subgroup of E ( F q ) {\displaystyle E(\mathbb {F} _{q})}![{\displaystyle E(\mathbb {F} _{q})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/211791ca6b9e75649feeba5dd7ec52de98c85d77), it follows from [Lagrange's theorem](https://en.wikipedia.org/wiki/Lagrange%27s_theorem_(group_theory)) that the number h = 1 n | E ( F q ) | {\displaystyle h={\frac {1}{n}}|E(\mathbb {F} _{q})|}![{\displaystyle h={\frac {1}{n}}|E(\mathbb {F} _{q})|}](https://wikimedia.org/api/rest_v1/media/math/render/svg/48abe43eaccd9013d70e34ea9c60ddae3865c7a2) is an integer. In cryptographic applications, this number _h_, called the _cofactor_, is usually small, ideally 1. Protocols using curves with cofactors greater than 1 must handle the cofactor appropriately. To summarize: in the prime case, the domain parameters are ( p , a , b , G , n , h ) {\displaystyle (p,a,b,G,n,h)}![{\displaystyle (p,a,b,G,n,h)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/855fbb66e0a1bf31aa7f20678c781678270bb231); in the binary case, they are ( m , f , a , b , G , n , h ) {\displaystyle (m,f,a,b,G,n,h)}![{\displaystyle (m,f,a,b,G,n,h)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/93f5549823023038c72ec57dba5ef4cc71f2ad7c).

Unless there is an assurance that domain parameters were generated by a party trusted with respect to their use, the domain parameters _must_ be validated before use.

The generation of domain parameters is not usually done by each participant because this involves computing [the number of points on a curve](https://en.wikipedia.org/wiki/Counting_points_on_elliptic_curves) which is time-consuming and troublesome to implement. As a result, several standard bodies published domain parameters of elliptic curves for several common field sizes. Such domain parameters are commonly known as "standard curves" or "named curves"; a named curve can be referenced either by name or by the unique [object identifier](https://en.wikipedia.org/wiki/Object_identifier) defined in the standard documents:

- ECC Brainpool ([RFC](https://en.wikipedia.org/wiki/RFC_(identifier)) [5639](https://www.rfc-editor.org/rfc/rfc5639)), [ECC Brainpool Standard Curves and Curve Generation](http://www.ecc-brainpool.org/download/Domain-parameters.pdf) [Archived](https://web.archive.org/web/20180417212206/http://www.ecc-brainpool.org/download/Domain-parameters.pdf) 2018-04-17 at the [Wayback Machine](https://en.wikipedia.org/wiki/Wayback_Machine)[[ 19 ]](#cite_note-19)[[ 20 ]](#cite_note-20)

SECG test vectors are also available.[[ 21 ]](#cite_note-21) NIST has approved many SECG curves, so there is a significant overlap between the specifications published by NIST and SECG. EC domain parameters may be specified either by value or by name.

If, despite the preceding admonition, one decides to construct one's own domain parameters, one should select the underlying field and then use one of the following strategies to find a curve with appropriate (i.e., near prime) number of points using one of the following methods:

- Select a random curve and use a general point-counting algorithm, for example, [Schoof's algorithm](https://en.wikipedia.org/wiki/Schoof%27s_algorithm) or the [Schoof–Elkies–Atkin algorithm](https://en.wikipedia.org/wiki/Schoof%E2%80%93Elkies%E2%80%93Atkin_algorithm),
- Select a random curve from a family which allows easy calculation of the number of points (e.g., [Koblitz curves](https://en.wikipedia.org/w/index.php?title=Koblitz_curve&action=edit&redlink=1)), or
- Select the number of points and generate a curve with this number of points using the _complex multiplication_ technique.[[ 22 ]](#cite_note-22)

Several classes of curves are weak and should be avoided:

- Curves over F 2 m {\displaystyle \mathbb {F} _{2^{m}}}![{\displaystyle \mathbb {F} _{2^{m}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/950de5de23e6ba61c1a5186dae752ae92ff4870e) with non-prime _m_ are vulnerable to [Weil descent](https://en.wikipedia.org/wiki/Weil_descent) attacks.[[ 23 ]](#cite_note-23)[[ 24 ]](#cite_note-24)
- Curves such that _n_ divides p B − 1 {\displaystyle p^{B}-1}![{\displaystyle p^{B}-1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/8e4b00cdb3241bd583e5edb55df1fdbd32613753) (where _p_ is the characteristic of the field: _q_ for a prime field, or 2 {\displaystyle 2}![{\displaystyle 2}](https://wikimedia.org/api/rest_v1/media/math/render/svg/901fc910c19990d0dbaaefe4726ceb1a4e217a0f) for a binary field) for sufficiently small _B_ are vulnerable to Menezes–Okamoto–Vanstone (MOV) attack[[ 25 ]](#cite_note-25)[[ 26 ]](#cite_note-26) which applies usual [discrete logarithm problem](https://en.wikipedia.org/wiki/Discrete_logarithm_problem) (DLP) in a small-degree extension field of F p {\displaystyle \mathbb {F} _{p}}![{\displaystyle \mathbb {F} _{p}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/2d35035371db7bee93733c68c1802114c17d8bb4) to solve ECDLP. The bound _B_ should be chosen so that [discrete logarithms](https://en.wikipedia.org/wiki/Discrete_logarithm) in the field F p B {\displaystyle \mathbb {F} _{p^{B}}}![{\displaystyle \mathbb {F} _{p^{B}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/52ce10a03eee6eec8cedaa63a1470fa5b0566948) are at least as difficult to compute as discrete logs on the elliptic curve E ( F q ) {\displaystyle E(\mathbb {F} _{q})}![{\displaystyle E(\mathbb {F} _{q})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/211791ca6b9e75649feeba5dd7ec52de98c85d77).[[ 27 ]](#cite_note-27)
- Curves such that | E ( F q ) | = q {\displaystyle |E(\mathbb {F} _{q})|=q}![{\displaystyle |E(\mathbb {F} _{q})|=q}](https://wikimedia.org/api/rest_v1/media/math/render/svg/742e321d63fb260bbdb28d431e643d3a895b19a3) are vulnerable to the attack that maps the points on the curve to the additive group of F q {\displaystyle \mathbb {F} _{q}}![{\displaystyle \mathbb {F} _{q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dbb96e056c071d13fc7702013f9273e7f5cd88a7).[[ 28 ]](#cite_note-28)[[ 29 ]](#cite_note-29)[[ 30 ]](#cite_note-30)

### Key sizes

Because all the fastest known algorithms that allow one to solve the ECDLP ([baby-step giant-step](https://en.wikipedia.org/wiki/Baby-step_giant-step), [Pollard's rho](https://en.wikipedia.org/wiki/Pollard%27s_rho_algorithm_for_logarithms), etc.), need O ( n ) {\displaystyle O({\sqrt {n}})}![{\displaystyle O({\sqrt {n}})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f5526ab1252c0f682bbe07c0ad67c0f29de5522b) steps, it follows that the size of the underlying field should be roughly twice the security parameter. For example, for 128-bit security one needs a curve over F q {\displaystyle \mathbb {F} _{q}}![{\displaystyle \mathbb {F} _{q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dbb96e056c071d13fc7702013f9273e7f5cd88a7), where q ≈ 2 256 {\displaystyle q\approx 2^{256}}![{\displaystyle q\approx 2^{256}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/ab29b541de93af75bb5724e6be7b9985ece02a8e). This can be contrasted with finite-field cryptography (e.g., [DSA](https://en.wikipedia.org/wiki/Digital_Signature_Algorithm)) which requires[[ 31 ]](#cite_note-31) 3072-bit public keys and 256-bit private keys, and integer factorization cryptography (e.g., [RSA](https://en.wikipedia.org/wiki/RSA_(algorithm))) which requires a 3072-bit value of _n_, where the private key should be just as large. However, the public key may be smaller to accommodate efficient encryption, especially when processing power is limited.

Historic public ECDLP challenge records include a 112-bit key for the prime field case and a 109-bit key for the binary field case. For the prime field case, this was broken in July 2009 using a cluster of over 200 [PlayStation 3](https://en.wikipedia.org/wiki/PlayStation_3) game consoles and could have been finished in 3.5 months using this cluster when running continuously.[[ 32 ]](#cite_note-32) The binary field case was broken in April 2004 using 2600 computers over 17 months.[[ 33 ]](#cite_note-33) The binary-field ECC2K-130 challenge has also been targeted by distributed computation using CPUs, GPUs, and FPGAs.[[ 34 ]](#cite_note-34)

### Projective coordinates

A close examination of the addition rules shows that in order to add two points, one needs not only several additions and multiplications in F q {\displaystyle \mathbb {F} _{q}}![{\displaystyle \mathbb {F} _{q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dbb96e056c071d13fc7702013f9273e7f5cd88a7) but also an [inversion](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) operation. The [inversion](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) (for given x ∈ F q {\displaystyle x\in \mathbb {F} _{q}}![{\displaystyle x\in \mathbb {F} _{q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cbe47674612548295c5c24f518686e99cfbe17b8) find y ∈ F q {\displaystyle y\in \mathbb {F} _{q}}![{\displaystyle y\in \mathbb {F} _{q}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f447d31b715006568a1815459b3cc9087cb2ffb5) such that x y = 1 {\displaystyle xy=1}![{\displaystyle xy=1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/dc7028e7e873eb4ec50f53be53ad478ded8351c1)) is one to two orders of magnitude slower[[ 35 ]](#cite_note-35) than multiplication. However, points on a curve can be represented in different coordinate systems which do not require an [inversion](https://en.wikipedia.org/wiki/Modular_multiplicative_inverse) operation to add two points. Several such systems were proposed: in the _projective_ system each point is represented by three coordinates ( X , Y , Z ) {\displaystyle (X,Y,Z)}![{\displaystyle (X,Y,Z)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/15fcf4aac62f9533d646603bdc5a9cf76ce95c23) using the following relation: x = X Z {\displaystyle x={\frac {X}{Z}}}![{\displaystyle x={\frac {X}{Z}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a128a5b548d8d9b23c2fa0446768a61cb0dc0853), y = Y Z {\displaystyle y={\frac {Y}{Z}}}![{\displaystyle y={\frac {Y}{Z}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/f54ff3015e02cd67e29a3eaef73054ec56ea1432); in the _Jacobian system_ a point is also represented with three coordinates ( X , Y , Z ) {\displaystyle (X,Y,Z)}![{\displaystyle (X,Y,Z)}](https://wikimedia.org/api/rest_v1/media/math/render/svg/15fcf4aac62f9533d646603bdc5a9cf76ce95c23), but a different relation is used: x = X Z 2 {\displaystyle x={\frac {X}{Z^{2}}}}![{\displaystyle x={\frac {X}{Z^{2}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9245e48cc26c553bd4d2718d2f98e4ac9044e5c1), y = Y Z 3 {\displaystyle y={\frac {Y}{Z^{3}}}}![{\displaystyle y={\frac {Y}{Z^{3}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/4c41c0f3df23d36c9f6fdcf66eecce7aa777974b); in the _López–Dahab system_ the relation is x = X Z {\displaystyle x={\frac {X}{Z}}}![{\displaystyle x={\frac {X}{Z}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a128a5b548d8d9b23c2fa0446768a61cb0dc0853), y = Y Z 2 {\displaystyle y={\frac {Y}{Z^{2}}}}![{\displaystyle y={\frac {Y}{Z^{2}}}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/cd4a44331a28859d2de621c25aa829015e8998ad); in the _modified Jacobian_ system the same relations are used but four coordinates are stored and used for calculations ( X , Y , Z , a Z 4 ) {\displaystyle (X,Y,Z,aZ^{4})}![{\displaystyle (X,Y,Z,aZ^{4})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/791891184fae2f51ebc3c61ce19f5fae0754470c); and in the _Chudnovsky Jacobian_ system five coordinates are used ( X , Y , Z , Z 2 , Z 3 ) {\displaystyle (X,Y,Z,Z^{2},Z^{3})}![{\displaystyle (X,Y,Z,Z^{2},Z^{3})}](https://wikimedia.org/api/rest_v1/media/math/render/svg/244b32573250cb250e5e3ef292c60490d2ead2fb). Note that there may be different naming conventions, for example, [IEEE P1363](https://en.wikipedia.org/wiki/IEEE_P1363)-2000 standard uses "projective coordinates" to refer to what is commonly called Jacobian coordinates. An additional speed-up is possible if mixed coordinates are used.[[ 36 ]](#cite_note-36)

### Fast reduction

Reduction modulo _p_ (which is needed for addition and multiplication) can be executed much faster if the prime _p_ is a [pseudo-Mersenne prime](https://en.wikipedia.org/wiki/Pseudo-Mersenne_prime) (Solinas prime), that is p ≈ 2 d {\displaystyle p\approx 2^{d}}![{\displaystyle p\approx 2^{d}}](https://wikimedia.org/api/rest_v1/media/math/render/svg/db99547ffde5293fae68fffc55c22ace3b80cc5b); for example, p = 2 521 − 1 {\displaystyle p=2^{521}-1}![{\displaystyle p=2^{521}-1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/9c524daa1c5aeeaf5691344d68a5ac15c673c390) (P-521) or p = 2 256 − 2 32 − 2 9 − 2 8 − 2 7 − 2 6 − 2 4 − 1. {\displaystyle p=2^{256}-2^{32}-2^{9}-2^{8}-2^{7}-2^{6}-2^{4}-1.}![{\displaystyle p=2^{256}-2^{32}-2^{9}-2^{8}-2^{7}-2^{6}-2^{4}-1.}](https://wikimedia.org/api/rest_v1/media/math/render/svg/03f7d3c4ad1b6d755f3ceb34b2695954ec24bc34) Compared to [Barrett reduction](https://en.wikipedia.org/wiki/Barrett_reduction), there can be an order of magnitude speed-up.[[ 37 ]](#cite_note-37) The speed-up here is a practical rather than theoretical one, and derives from the fact that the moduli of numbers against numbers near powers of two can be performed efficiently by computers operating on binary numbers with [bitwise operations](https://en.wikipedia.org/wiki/Bitwise_operation).

Other widely deployed curves also use primes with special forms that allow efficient reduction, such as p = 2 255 − 19 {\displaystyle p=2^{255}-19}![{\displaystyle p=2^{255}-19}](https://wikimedia.org/api/rest_v1/media/math/render/svg/84df417f25210afd283f9bc10a4270b0444f8b06) for Curve25519 and 2 448 − 2 224 − 1 {\displaystyle 2^{448}-2^{224}-1}![{\displaystyle 2^{448}-2^{224}-1}](https://wikimedia.org/api/rest_v1/media/math/render/svg/a7dac11fc4a37618d0949b5ed9ee69a686eab6af) for Curve448.[[ 38 ]](#cite_note-SafeCurves-38)

## Security

### Side-channel attacks

Unlike most other [discrete logarithm problem](https://en.wikipedia.org/wiki/Discrete_logarithm_problem) (DLP) systems (where it is possible to use the same procedure for squaring and multiplication), the EC addition is significantly different for doubling (_P_ = _Q_) and general addition (_P_ ≠ _Q_) depending on the coordinate system used. Consequently, it is important to counteract [side-channel attacks](https://en.wikipedia.org/wiki/Side-channel_attack) (e.g., timing or [simple/differential power analysis attacks](https://en.wikipedia.org/wiki/Power_analysis)) using, for example, fixed pattern window (a.k.a. comb) methods[_[clarification needed](https://en.wikipedia.org/wiki/Wikipedia:Please_clarify)_][[ 39 ]](#cite_note-39) (note that this does not increase computation time). Alternatively one can use an [Edwards curve](https://en.wikipedia.org/wiki/Edwards_curve); this is a special family of elliptic curves for which doubling and addition can be done with the same operation.[[ 40 ]](#cite_note-40) Another concern for ECC-systems is the danger of [fault attacks](https://en.wikipedia.org/wiki/Differential_fault_analysis), especially when running on [smart cards](https://en.wikipedia.org/wiki/Smart_card).[[ 41 ]](#cite_note-41)

### Backdoors

Cryptographic experts have expressed concerns that the [National Security Agency](https://en.wikipedia.org/wiki/National_Security_Agency) has inserted a [kleptographic](https://en.wikipedia.org/wiki/Kleptographic) backdoor into at least one elliptic curve-based pseudo random generator.[[ 42 ]](#cite_note-42) Internal memos leaked by former NSA contractor [Edward Snowden](https://en.wikipedia.org/wiki/Edward_Snowden) suggest that the NSA put a backdoor in the [Dual EC DRBG](https://en.wikipedia.org/wiki/Dual_EC_DRBG) standard.[[ 43 ]](#cite_note-43) One analysis of the possible backdoor concluded that an adversary in possession of the algorithm's secret key could obtain encryption keys given only 32 bytes of PRNG output.[[ 44 ]](#cite_note-44)

The SafeCurves project catalogs curves that are easy to implement securely and are designed in a fully publicly verifiable way to minimize the chance of a backdoor.[[ 45 ]](#cite_note-45)

### Quantum computing attack

[Shor's algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm) can be used to break elliptic curve cryptography by computing discrete logarithms on a sufficiently large fault-tolerant [quantum computer](https://en.wikipedia.org/wiki/Quantum_computing). Published quantum resource estimates for breaking a curve with a 256-bit modulus (128-bit security level) include 2330 logical [qubits](https://en.wikipedia.org/wiki/Qubits) and 126 billion [Toffoli gates](https://en.wikipedia.org/wiki/Toffoli_gate).[[ 46 ]](#cite_note-46) For the binary elliptic curve case, 906 logical qubits are necessary to break 128 bits of security.[[ 47 ]](#cite_note-47) These estimates do not imply that current quantum computers can break deployed ECC systems, but they are a reason for migration planning.

In August 2024, NIST approved the first three Federal Information Processing Standards for [post-quantum cryptography](https://en.wikipedia.org/wiki/Post-quantum_cryptography): FIPS 203 for ML-KEM, FIPS 204 for ML-DSA, and FIPS 205 for SLH-DSA.[[ 48 ]](#cite_note-nist-pqc-fips-48) NIST describes these standards as principal post-quantum standards for key establishment and digital signatures.[[ 49 ]](#cite_note-nist-pqc-project-49) NSA's CNSA 2.0 guidance similarly identifies quantum-resistant algorithms for national security systems and states that CNSA 1.0 compliance remains required during the transition.[[ 7 ]](#cite_note-nsa-cnsa2-7)

[Supersingular Isogeny Diffie–Hellman Key Exchange](https://en.wikipedia.org/wiki/Supersingular_isogeny_key_exchange) was proposed as a [post-quantum](https://en.wikipedia.org/wiki/Post-quantum_cryptography) form of elliptic-curve-based key exchange using [isogenies](https://en.wikipedia.org/wiki/Isogenies).[[ 50 ]](#cite_note-50) However, new classical attacks undermined the security of this protocol.[[ 51 ]](#cite_note-51)

In August 2015, the NSA announced that it planned to transition "in the not distant future" to a new cipher suite that is resistant to [quantum](https://en.wikipedia.org/wiki/Quantum_computing) attacks. "Unfortunately, the growth of elliptic curve use has bumped up against the fact of continued progress in the research on quantum computing, necessitating a re-evaluation of our cryptographic strategy."[[ 13 ]](#cite_note-nsaquantum-13)

### Invalid curve attack

ECC implementations can be susceptible to invalid-curve attacks if they multiply a secret scalar by attacker-supplied points without verifying that the points lie on the intended curve and in the correct subgroup. In such attacks, repeated operations on invalid or small-order points can leak information about the private scalar. In 2019, an invalid-curve attack against AMD Secure Encrypted Virtualization was reported to recover a Platform Diffie–Hellman (PDH) private key.[[ 52 ]](#cite_note-Cohen,_Seclist,_2019-52)

## Alternative representations

Alternative representations of elliptic curves include:

- [Hessian curves](https://en.wikipedia.org/wiki/Hessian_curves)
- [Edwards curves](https://en.wikipedia.org/wiki/Edwards_curves)
- [Twisted curves](https://en.wikipedia.org/wiki/Twisted_curves)
- [Twisted Hessian curves](https://en.wikipedia.org/wiki/Twisted_Hessian_curves)
- [Twisted Edwards curve](https://en.wikipedia.org/wiki/Twisted_Edwards_curve)
- [Doubling-oriented Doche–Icart–Kohel curve](https://en.wikipedia.org/wiki/Doubling-oriented_Doche%E2%80%93Icart%E2%80%93Kohel_curve)
- [Tripling-oriented Doche–Icart–Kohel curve](https://en.wikipedia.org/wiki/Tripling-oriented_Doche%E2%80%93Icart%E2%80%93Kohel_curve)
- [Jacobian curve](https://en.wikipedia.org/wiki/Jacobian_curve)
- [Montgomery curves](https://en.wikipedia.org/wiki/Montgomery_curve)

## See also

## Notes

## References

- [Standards for Efficient Cryptography Group (SECG)](https://en.wikipedia.org/wiki/SECG), [SEC 1: Elliptic Curve Cryptography](http://www.secg.org/sec1-v2.pdf), Version 1.0, September 20, 2000. ([archived](https://web.archive.org/web/20141111191126/http://www.secg.org/sec1-v2.pdf) as of Nov 11, 2014)
- D. Hankerson, A. Menezes, and S.A. Vanstone, _Guide to Elliptic Curve Cryptography_, Springer-Verlag, 2004.
- I. Blake, G. Seroussi, and N. Smart, _Elliptic Curves in Cryptography_, London Mathematical Society 265, Cambridge University Press, 1999.
- I. Blake, G. Seroussi, and N. Smart, editors, _Advances in Elliptic Curve Cryptography_, London Mathematical Society 317, Cambridge University Press, 2005.
- L. Washington, _Elliptic Curves: Number Theory and Cryptography_, Chapman & Hall / CRC, 2003.
- [The Case for Elliptic Curve Cryptography](https://web.archive.org/web/20090117023500/http://www.nsa.gov/business/programs/elliptic_curve.shtml), National Security Agency (archived January 17, 2009)
- [Online Elliptic Curve Cryptography Tutorial](http://www.certicom.com/index.php/ecc-tutorial), Certicom Corp. (archived [here](https://web.archive.org/web/20160309033943/http://certicom.com/index.php/ecc-tutorial) as of March 3, 2016)
- K. Malhotra, S. Gardner, and R. Patz, Implementation of Elliptic-Curve Cryptography on Mobile Healthcare Devices, Networking, Sensing and Control, 2007 IEEE International Conference on, London, 15–17 April 2007 Page(s):239–244
- Saikat Basu, [A New Parallel Window-Based Implementation of the Elliptic Curve Point Multiplication in Multi-Core Architectures](http://ijns.jalaxy.com.tw/contents/ijns-v14-n2/ijns-2012-v14-n2-p101-108.pdf), International Journal of Network Security, Vol. 13, No. 3, 2011, Page(s):234–241 (archived [here](https://web.archive.org/web/20160304121101/http://ijns.jalaxy.com.tw/contents/ijns-v14-n2/ijns-2012-v14-n2-p101-108.pdf) as of March 4, 2016)
- Christof Paar, Jan Pelzl, ["Elliptic Curve Cryptosystems"](https://archive.today/20121208212741/http://wiki.crypto.rub.de/Buch/movies.php), Chapter 9 of "Understanding Cryptography, A Textbook for Students and Practitioners". (companion web site contains online cryptography course that covers elliptic curve cryptography), Springer, 2009. (archived [here](https://archive.today/20121208212741/http://wiki.crypto.rub.de/Buch/movies.php) as of April 20, 2016)
- Luca De Feo, David Jao, Jerome Plut, [Towards quantum-resistant cryptosystems from supersingular elliptic curve isogenies](http://eprint.iacr.org/2011/506), Springer 2011. (archived [here](https://web.archive.org/web/20120507200407/http://eprint.iacr.org/2011/506) as of May 7, 2012)
- Gustavo Banegas, Daniel J. Bernstein, Iggy Van Hoof, Tanja Lange, [Concrete quantum cryptanalysis of binary elliptic curves](https://eprint.iacr.org/2020/1296), Springer 2020. (archived [here](https://eprint.iacr.org/2020/1296) as of June 1, 2020)

- [Jacques Vélu, Courbes elliptiques (...) , Société Mathématique de France, 57 , 1-152, Paris, 1978.](http://archive.numdam.org/ARCHIVE/MSMF/MSMF_1978__57_/MSMF_1978__57__1_0/MSMF_1978__57__1_0.pdf)

## External links

- [Elliptic Curves](https://crypto.stanford.edu/pbc/notes/elliptic/) at [Stanford University](https://en.wikipedia.org/wiki/Stanford_University)
- [Interactive introduction to elliptic curves and elliptic curve cryptography with Sage](https://web.archive.org/web/20120301091325/http://sagenb.org/home/pub/1126/) by [Maike Massierer](http://www.maths.unsw.edu.au/~maikemassierer/) and the [CrypTool](https://www.cryptool.org/en/) team
- [![Wikimedia Commons logo](https://upload.wikimedia.org/wikipedia/en/thumb/4/4a/Commons-logo.svg/40px-Commons-logo.svg.png)](https://en.wikipedia.org/wiki/File:Commons-logo.svg) Media related to [Elliptic curve](https://commons.wikimedia.org/wiki/Elliptic_curve) at Wikimedia Commons