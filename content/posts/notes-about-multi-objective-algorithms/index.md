+++
title = "Notes about multi-objective evolutionary algorithms"
date = "2020-09-02"
draft = true
+++

Hi everyone! I’m decided to write a few notes about the topic that I’m studying ate the moment. Would not be a big tutorial, just notes and observations.

Now I’m trying to undestand more about multi-objective evolutionary algorithms (MOEAs). I’m reading _A scalable multi-objective test problem toolkit_ that presents a new toolkit for creating scalable multi-objetive test problems: the Wailking Fish Group (WFG) toolkit :)

This toolkit allows to build scalable test problems with any number of objectives, you can customise modality and separability.

> **customise modality? separability?** **multi-objective optimisation problem**

### terminology

Consider a multi-objetive optimisation problem given in terms of a _search space_ of allowed values _n_ parameters _x1, x2, …, xn_ and a vector of _M_ objetive functions _{f1, … , fm}_ mapping parameters vectors into fitness space.

- _fitness landscape_: the mapping from the search space to fitness space

The aim: **to find the set of optimal tread-off solutions know as Pareto optimal set**.

- _pareto optimal set_: is the set of all pareto optimal parameter vectores, and the corresponding set of objective vectors is the _pareto optimal front_.

- the _pareto optimal set_ is a subset of the search space.
- the _pareto optimal front_ is a subset of the fitness space.
- the following types of relationsships are useful because they allow us to separate the convergence and spread aspects of sets of solution for a problem

- a _distance parameters_ is one that when modified only ever results in a dominated, dominating, or equivalent parameters vector.
- a _position parameter_ is one that when modified only ever results in a incomparable or equivalent parameters vector

> multi objective vs many

DTLZ test suite has limitations, none of its problems is deceptive, non of its problems is non separable, and the number of position parameters is always fixed relative to the number of objective

> degenerate pareto optimal fronts: is a front that is a of lower dimension that the objective space in which it is embedded, less one

### wfg tookit
