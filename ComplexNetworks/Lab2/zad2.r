library(igraph)
set.seed(111)

#2a
n <- 1000
m <- 3
graph <- barabasi.game(n, m, directed = FALSE)

#2b
plot(graph,
    vertex.label = NA,
    vertex.size = 4,
    layout = layout.fruchterman.reingold)

#2c
closeness_values <- closeness(graph)

most_central_node_index <- which.max(closeness_values)
most_central_node_number <- most_central_node_index - 1
cat("\nNode number:", most_central_node_number)

#2d
diameter <- diameter(graph)

cat("\nŚrednica:", diameter)

#2e

cat("\n")