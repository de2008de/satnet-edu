# Lecture 04: Dynamics, Handover, and Performance

[View the slides](lecture-04.pdf) · [Edit the Beamer source](main.tex)

One title slide and nine teaching slides, in English. Instructor:
Yi Ching (David) Chou.

1. Link and route changes across snapshots
2. Overlap, preparation time, and access handover
3. Elevation, remaining contact time, and switching policies
4. Propagation changes when routes switch
5. Propagation, transmission, queueing, and processing
6. Queue growth during an outage and draining after recovery
7. Bandwidth-delay product and data in flight
8. Packet reordering across paths
9. Sampling intervals and missed interruptions

Students should be able to read contact timelines, distinguish instantaneous
reachability from service continuity, and calculate simple delay, queue, and
window examples. Every numerical time plot is a constructed example, not an
operator measurement or a claim about current commercial service.

The handover preparation, fluid queue, send-window limit, and packet-arrival
examples explain networking concepts beyond SatNet Edu's implemented model.
The simulator records available links and instantaneous routes. It does not
simulate handover control, traffic, queues, or transport protocols.

Build from the repository root with `.\teaching\make.cmd lecture-04` on Windows
or `make -C teaching lecture-04` on Linux/macOS. See the
[course build guide](../README.md#build-the-slides).

## Instructor background

- [RFC 2488, Section 2](https://www.rfc-editor.org/rfc/rfc2488.html#section-2): background on propagation, feedback time, and bandwidth-delay product. The lecture uses these general concepts, not the document's historical equipment parameters or a current TCP configuration recommendation.
- [SatNet Edu model and sampling](../../docs/MODEL.md)

Instructor notes in `main.tex` state the assumptions and calculations for each
example. Lecture 05 turns the sampling and metric distinctions into an experiment.
