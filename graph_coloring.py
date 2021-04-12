from igraph import *
from graphframes import GraphFrame
from graphframes.lib import AggregateMessages as AM
from pyspark.sql import SparkSession
from pyspark.sql import functions as F, types
from typing import Optional

spark = SparkSession.builder.appName("graph-coloring").getOrCreate()


def plot_graph(g: GraphFrame, file_name: str) -> None:
    """Plots a given Graphframe to a png file
    :param g: The graph as Graphframe object
    :param file_name: The name of the output file
    :return: None
    """
    ver_pd = g.vertices.toPandas()
    ed_pd = g.edges.toPandas()
    ig = Graph.DataFrame(edges=ed_pd, directed=False, vertices=ver_pd)
    id_gen = UniqueIdGenerator()
    color_indices = [id_gen.add(value) for value in ver_pd["color"]]
    palette = ClusterColoringPalette(len(id_gen))
    colors = [palette[index] for index in color_indices]
    ig.vs["color"] = colors

    plot(ig, target="/vagrant/" + file_name + ".png", vertex_label=ver_pd["id"])


# Read data from csv files
vertices = spark.read.csv("/vagrant/datasets/nodes.csv", header=True)
edges = spark.read.csv("/vagrant/datasets/edges.csv", header=True)

# Add extra columns
vertices = vertices.withColumn("maxima", F.lit(True))
vertices = vertices.withColumn("color", F.lit(-1))
cached_vertices = AM.getCachedDataFrame(vertices)

# Create and print information on the respective GraphFrame
g = GraphFrame(cached_vertices, edges)
g.vertices.show()
g.edges.show()
g.degrees.show()

plot_graph(g, "initial_graph")


def prune_vertices(vertex_id, color) -> Optional[int]:
    """Returns the vertex id if the vertex has no color assigned yet.
    :param vertex_id: The vertex id
    :param color: The current color of the vertex
    :return: vertex_id or None
    """
    return vertex_id if color == -1 else None


prune_vertices_udf = F.udf(prune_vertices, types.StringType())


def calculate_color(
    vertex_id: int, current_color: int, maxima: bool, messages: list, superstep: int
) -> dict:
    """UDF that calculates the color of the nodes. Based on Local Maxima First algorithm
    :param vertex_id: The id of the node/vertex
    :param current_color: The current color of the vertex
    :param maxima: Flag that indicates if the node is maxima
    :param messages: List that contains the neighbor ids that send message
    :param superstep: The superstep number
    :return: Dictionary that contains the new color and the status of maxima
    """
    # Return if you have already been colored!
    if current_color != -1:
        return {"id": id, "new_color": current_color, "new_maxima": True}
    # Local Maxima first interal procedure
    for message in messages:
        if vertex_id < message:
            maxima = False
            break
    return (
        {"id": id, "new_color": superstep, "new_maxima": maxima}
        if maxima
        else {"id": id, "new_color": current_color, "new_maxima": True}
    )


color_type = types.StructType(
    [
        types.StructField("id", types.StringType()),
        types.StructField("new_color", types.IntegerType()),
        types.StructField("new_maxima", types.BooleanType()),
    ]
)
calculate_color_udf = F.udf(calculate_color, color_type)

superstep = 0
while True:
    msg_dst = prune_vertices_udf(AM.src["id"], AM.src["color"])
    msg_src = prune_vertices_udf(AM.dst["id"], AM.dst["color"])

    ids = g.aggregateMessages(
        F.collect_set(AM.msg).alias("ids"), sendToSrc=msg_src, sendToDst=msg_dst
    )

    new_vertices = (
        g.vertices.join(ids, on="id", how="left_outer")
        .withColumn(
            "new_values",
            calculate_color_udf("id", "color", "maxima", "ids", F.lit(superstep)),
        )
        .select(
            "id",
            "name",
            "maxima",
            "color",
            "new_values.new_maxima",
            "new_values.new_color",
        )
        .drop("ids", "maxima", "color")
        .withColumnRenamed("new_color", "color")
        .withColumnRenamed("new_maxima", "maxima")
    )
    # Save the changes
    cached_new_vertices = AM.getCachedDataFrame(new_vertices)
    g_new = GraphFrame(cached_new_vertices, g.edges)

    superstep += 1
    g = g_new

    g.vertices.show()

    # In order to terminate this algorithm, make sure that all vertices have an assigned color
    if not g.vertices.filter(F.col("color").isin(-1)).select("color").collect():
        break

plot_graph(g, "final_graph")
