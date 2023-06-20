library(igraph)
set.seed(111)

#3a
data_frame <- read.table("foodweb_baydry",
    header = FALSE,
    col.names = c("source", "target", "weight"),
    sep = "")
data_frame <- subset(data_frame, select = c("source", "target"))
print(head(data_frame, n = 20))

#3b
graph <- graph_from_edgelist(as.matrix(data_frame), directed = FALSE)
plot(graph,
    vertex.size = 4,
    vertex.label = NA,
    layout = layout.fruchterman.reingold)

#3c
cat("\n\nBefore:", vcount(graph))
cat("\nBefore:", ecount(graph))

graph <- simplify(graph)


cat("\nAfter:", vcount(graph))
cat("\nAfter:", ecount(graph))

#3d
degrees <- degree(graph)
betweenness <- betweenness(graph)
closeness <- closeness(graph)
hist(degrees, xlab = "Stopień węzłów", ylab = "Liczba węzłów")
hist(betweenness, xlab = "Betweenness", ylab = "Liczba węzłów")
hist(closeness, xlab = "Closeness", ylab = "Liczba węzłów")

cat("\n\nTau between-closeness",
    cor(rank(betweenness), rank(closeness), method = "kendall"))
cat("\nTau between-degrees",
    cor(rank(betweenness), rank(degrees), method = "kendall"))
cat("\nTau closeness-degrees",
    cor(rank(closeness), rank(degrees), method = "kendall"))

#3e
components <- components(graph)
cat("\n\nLiczba komponentów w grafie wynosi:", components$no)

#3f
diameter <- diameter(graph)
avg_path <- average.path.length(graph)
cat("\n\nDiameter", diameter)
cat("\nAvg path", avg_path)

#3g
dist_matrix <- distances(graph)
hist(dist_matrix, xlab = "Długość ścieżki", ylab = "Liczba par wierzchołków")

clustering_coefficient <- transitivity(graph)
hist(clustering_coefficient,
    xlab = "Współczynnik grupowania",
    ylab = "Liczba wierzchołków")

cat("\n")