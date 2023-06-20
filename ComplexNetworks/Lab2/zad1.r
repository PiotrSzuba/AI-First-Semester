library(igraph)
set.seed(111)

#1a
n <- 100
p <- 0.03


graph <- erdos.renyi.game(n, p)

#1b
print("\nWierzchołki:\n")
cat(as.character(V(graph)), "\n")

print("\nKrawędzie:\n")
cat(as.character(get.edgelist(graph)), "\n")

#1c
set_edge_attr(graph, "weight", value = runif(ecount(graph), 0.01, 1))

#1d
clustering_coefficient <- transitivity(graph)
cat("Współczynnik grupowania węzłów:\n")
cat(clustering_coefficient, "\n")

degrees <- degree(graph)
hist(degree(graph, mode = "all"),
    main = "Dystrybucja stopni węzła",
    xlab = "Stopień")

#1e
components <- components(graph)
num_components <- length(components$no)
print(paste("Liczba komponentów w grafie wynosi:", num_components))

#1f
plot(graph, vertex.size = degree(graph), vertex.label = NA)