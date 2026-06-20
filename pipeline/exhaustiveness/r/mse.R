#!/usr/bin/env Rscript
# Advanced multi-source MSE for the exhaustiveness framework.
#
# Contract: reads a JSON object from the file given as argv[1]:
#   { "k": <int>, "patterns": [[b1,...,bk, freq], ...] }
# (the all-zero pattern must be omitted). Writes a JSON object to stdout:
#   { "rcapture": {n_hat, ci_low, ci_high, bic, model},
#     "lcmcr":    {n_hat, ci_low, ci_high} | {error},
#     "status": "ok" }
#
# Uses Rcapture::closedpMS.t (log-linear model selection, the §2.3 cross-check)
# and LCMCR (latent-class Bayesian, heterogeneity-robust). Any model that fails
# is reported as {error} without aborting the others.

suppressWarnings(suppressMessages({
  ok_rcapture <- requireNamespace("Rcapture", quietly = TRUE)
  ok_lcmcr <- requireNamespace("LCMCR", quietly = TRUE)
  library(jsonlite)
}))

args <- commandArgs(trailingOnly = TRUE)
inp <- fromJSON(paste(readLines(args[[1]], warn = FALSE), collapse = ""))
k <- inp$k
mat <- inp$patterns                      # numeric matrix (rows x (k+1))
if (is.null(dim(mat))) mat <- matrix(mat, ncol = k + 1, byrow = TRUE)
storage.mode(mat) <- "double"

out <- list(status = "ok")

# --- Rcapture closedpMS.t (log-linear model selection) ---
out$rcapture <- tryCatch({
  if (!ok_rcapture) stop("Rcapture not installed")
  # maxorder=2 (pairwise interactions only) + stopiflong=FALSE so the model
  # search is bounded and runs for >=5 lists instead of refusing.
  res <- Rcapture::closedpMS.t(mat, dfreq = TRUE, maxorder = 2, stopiflong = FALSE)
  tab <- as.data.frame(res$results)
  # pick the model with the lowest BIC
  bic_col <- if ("BIC" %in% colnames(tab)) "BIC" else grep("BIC", colnames(tab), value = TRUE)[1]
  best <- which.min(tab[[bic_col]])
  abundance <- tab[["abundance"]][best]
  stderr <- tab[["stderr"]][best]
  list(
    n_hat = unname(abundance),
    ci_low = unname(abundance - 1.96 * stderr),
    ci_high = unname(abundance + 1.96 * stderr),
    bic = unname(tab[[bic_col]][best]),
    model = rownames(tab)[best]
  )
}, error = function(e) list(error = conditionMessage(e)))

# --- LCMCR (latent-class Bayesian, heterogeneity) ---
out$lcmcr <- tryCatch({
  if (!ok_lcmcr) stop("LCMCR not installed")
  # build a data.frame of factor capture columns expanded by frequency
  bits <- mat[, 1:k, drop = FALSE]
  freq <- mat[, k + 1]
  idx <- rep(seq_len(nrow(bits)), times = as.integer(freq))
  df <- as.data.frame(bits[idx, , drop = FALSE])
  colnames(df) <- paste0("L", seq_len(k))
  for (j in seq_len(k)) df[[j]] <- factor(df[[j]], levels = c(0, 1))
  set.seed(20260620)
  sampler <- LCMCR::lcmCR(df, tabular = FALSE, K = 5,
                          a_alpha = 0.25, b_alpha = 0.25,
                          seed = 20260620, buffer_size = 10000, thinning = 20)
  post <- LCMCR::lcmCR_PostSampl(sampler, burnin = 5000, samples = 8000, output = FALSE)
  list(
    n_hat = unname(median(post)),
    ci_low = unname(quantile(post, 0.025)),
    ci_high = unname(quantile(post, 0.975))
  )
}, error = function(e) list(error = conditionMessage(e)))

cat(toJSON(out, auto_unbox = TRUE, digits = 6))
