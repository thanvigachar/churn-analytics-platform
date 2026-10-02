# Results (auto-generated)

- Customer records: 7,043
- Overall churn rate: 26.5%
- Best model (ROC-AUC): logistic_regression (0.853)
- Recall at threshold 0.3: 92.2% (precision 42.3%)
- Expected monthly revenue at risk: $114,508
- High-risk active customers: 1002 ($77,223/month)
- Estimated impact at 20% save rate: $15,445/month (assumption, not a measured result)

## Model comparison
| model               |   threshold |   recall |   precision |    f1 |   roc_auc |
|:--------------------|------------:|---------:|------------:|------:|----------:|
| logistic_regression |         0.3 |    0.922 |       0.423 | 0.58  |     0.853 |
| logistic_regression |         0.4 |    0.896 |       0.475 | 0.621 |     0.853 |
| logistic_regression |         0.5 |    0.84  |       0.523 | 0.645 |     0.853 |
| random_forest       |         0.3 |    0.912 |       0.427 | 0.582 |     0.847 |
| random_forest       |         0.4 |    0.885 |       0.49  | 0.63  |     0.847 |
| random_forest       |         0.5 |    0.789 |       0.513 | 0.622 |     0.847 |
| gradient_boosting   |         0.3 |    0.762 |       0.523 | 0.62  |     0.848 |
| gradient_boosting   |         0.4 |    0.668 |       0.58  | 0.621 |     0.848 |
| gradient_boosting   |         0.5 |    0.543 |       0.663 | 0.597 |     0.848 |
