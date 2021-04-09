from graphframes import GraphFrame
from graphframes.lib import AggregateMessages as AM
from pyspark.sql import SparkSession
from pyspark.sql import functions as F, types

spark = SparkSession.builder.appName('graph-coloring').getOrCreate()

# Nodes
vertices = spark.createDataFrame([('1', 'Iron Man'),
                                  ('2', 'Cpt. America'),
                                  ('3', 'Thor'),
                                  ('4', 'Doctor Strange'),
                                  ('5', 'Scarlet Witch'),
                                  ('6', 'Groot')],
                                 ['id', 'name'])

# Some random associations between the vertices that form a connected graph.
edges = spark.createDataFrame([('1', '2'),
                               ('3', '2'),
                               ('4', '2'),
                               ('5', '2'),
                               ('5', '3'),
                               ('6', '2')],
                              ['src', 'dst'])

vertices = vertices.withColumn("maxima", F.lit(True))
vertices = vertices.withColumn("color", F.lit(-1))
cached_vertices = AM.getCachedDataFrame(vertices)

# Create and print information on the respective GraphFrame
g = GraphFrame(cached_vertices, edges)
g.vertices.show()
g.edges.show()
g.degrees.show()


def new_paths(vertices, color):
    return vertices if color == -1 else None


new_paths_udf = F.udf(new_paths, types.StringType())


def calculate_color(vertex_id, current_color, maxima, messages, superstep):
    # print('calculate', vertex_id, messages, maxima, superstep)
    # Return if you have already been colored!
    if current_color != -1:
        return {"id": id, "new_color": current_color, "new_maxima": True}
    # Local Maxima first interal procedure
    for message in messages:
        if vertex_id < message:
            print(vertex_id, message)
            maxima = False
            break
    return {"id": id, "new_color": superstep, "new_maxima": maxima} if maxima \
        else {"id": id, "new_color": current_color, "new_maxima": True}


color_type = types.StructType([types.StructField("id", types.StringType()),
                               types.StructField("new_color", types.IntegerType()),
                               types.StructField("new_maxima", types.BooleanType())])
calculate_color_udf = F.udf(calculate_color, color_type)

superstep = 0
while True:
    msg_dst = new_paths_udf(AM.src["id"], AM.src["color"])
    msg_src = new_paths_udf(AM.dst["id"], AM.dst["color"])

    ids = g.aggregateMessages(F.collect_set(AM.msg).alias("ids"), sendToSrc=msg_src, sendToDst=msg_dst)

    new_vertices = g.vertices.join(ids, on="id", how="left_outer") \
        .withColumn("new_values", calculate_color_udf("id", "color", "maxima", "ids", F.lit(superstep))) \
        .select("id", "maxima", "color", "new_values.new_maxima", "new_values.new_color") \
        .drop("ids", "maxima", "color") \
        .withColumnRenamed("new_color", "color") \
        .withColumnRenamed("new_maxima", "maxima") \

    cached_new_vertices = AM.getCachedDataFrame(new_vertices)
    g_new = GraphFrame(cached_new_vertices, g.edges)
    print("Updated Vertices")
    g_new.vertices.show()

    # In order to terminate this algorithm, make sure that all vertices have an assigned color
    if not g.vertices.filter(F.col('color').isin(-1)).select('color').collect():
        break

    superstep += 1
    g = g_new

