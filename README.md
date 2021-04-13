# Spark Graph Coloring

This project is an assignment for the M.Sc. course Analysis of Social Networks
More details about the task can be found [here](https://github.com/VangelisTsiatouras/spark-graph-coloring/blob/main/M222-Project01.pdf).

## Installation & Execution

In order to run the script initially you should install [Vagrant](https://www.vagrantup.com/docs/installation) on your machine.

Then you can build the VM by entering the following command (it will take some time to finish...):

```bash
vagrant up
```

After that, the VM can be accessed by entering:

```bash 
vagrant ssh
```

Finally, in order to execute the PySpark script run the following command:

```bash
~/spark-2.4.7-bin-hadoop2.7/bin/spark-submit --packages graphframes:graphframes:0.8.1-spark2.4-s_2.11 /vagrant/graph_coloring.py
```

## Examples

By applying Local Maxima First Algorithm in the distributed environment of Spark, this script can solve efficiently the
graph coloring problem even for large scale graphs. A small example is listed below.

![initial-graph](https://github.com/VangelisTsiatouras/spark-graph-coloring/blob/main/output_images/initial_graph.png)

![colored-graph](https://github.com/VangelisTsiatouras/spark-graph-coloring/blob/main/output_images/final_graph.png)
