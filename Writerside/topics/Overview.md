# Overview

Advancing IKEv2 for the Quantum Age: Challenges in Post-Quantum Cryptography Implementation on Constrained Networks

This project contains the necessary elements to set up and test the performance of an IPSEC tunnel that is 
IKEv2 protocol based and implements post-quantum cryptography for the key exchange and subsequent data packets.
This code repository was developed for our research project to explore the impacts of network degradation
on a simulated network running the IKEv2 protocol and quantum-resistant cryptography. 
Ultimately this code repository is a stepping stone to answer the question: 
At what points do various factors of network degradation cause IKEv2 to cease functioning?

## Team

The University of Alabama in Huntsville (UAH) - Team 4 Members:
- Julien C. Chalkley - [GitHubProfile](https://github.com/Jules2C)
- James D. Fluhler - [GitHubProfile](https://github.com/jfluhler)
- Kathryn Heard - 
- Leslie A. Hurst - [GitHubProfile](https://github.com/Lahurst)
- Evan C. Mitchell - [GitHubProfile](https://github.com/evanmitchell777)

- UAH Faculty Advisor: Dr. Bramwell Brizendine - [GitHubProfile](https://github.com/Bw3ll)
- Problem Mentor: Dr. Bill Layton, NSA

April 26, 2024


## Project Description

Description:
The impending presence of quantum computing threatens modern crypto systems, as the means by which most public 
cryptographic algorithms are secured does not adequately protect against quantum-enabled attacks. Current algorithms 
cannot keep communications secure in a post-quantum world; so it is now necessary to explore the implementation of 
quantum-resistant algorithms over our existing network infrastructure (Mailloux et al., p. 43). But quantum-resistant 
algorithms may have a different level of stability than existing algorithms when transmitted over the same infrastructure, 
thus it is critical for Information Security professionals to understand transmission behavior for post-quantum algorithms. 
Fortunately, there has been some research done on network-level key exchange protocols. In an article titled 
“Analysis of Network-level Key Exchange Protocols in the Post-Quantum Era” different protocols were tested in 
order to find the best quantum-resistant protocol. 

This project will explore the transmission behaviors of the 
IKEv2 protocol under constrained network conditions, seeking to find the point at which various network conditions 
cause IKEv2 to fail. With this information, IT professionals will be better informed about the minimum network 
requirements to implement IKEv2 on their networks and help nurture a quantum-resistant security posture.

