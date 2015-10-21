error.bars <- function(xs, ys, ses) {
    mapply(function(x, y, se) {
        arrows(x, y - se, x, y + se, angle = 90, code = 3, length = 0.1)
    }, xs, ys, ses)
    return()
}
se <- function(x) { sd(x)/sqrt(length(x))}

dat <- read.csv('full.csv')
with(dat, table(supervisor, searchers, rescuers))
means <- aggregate(time ~ supervisor + searchers + rescuers, data = dat, FUN=mean)
ses <- aggregate(time ~ supervisor + searchers + rescuers, data = dat, FUN=se)

b <- barplot(matrix(means$time, nrow = 2, byrow = F), beside = T,
             names.arg = c("1/1", "3/3", "6/3"),
             legend.text = c("mothership", "supervisor"),
             ylim = c(0, 550),
             ylab = "Mean rescue time",
             xlab = "searchers/rescuers",
             main = "Mean reaction times vs. condition")
error.bars(b, means$time, ses$time)
