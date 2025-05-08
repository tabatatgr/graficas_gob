rm(list = ls()) 
pacman::p_load(tidyverse, showtext, ggtext, readxl, scales)

set.seed(1)
df <- tibble(
  fecha = seq(as.Date("2018-01-01"), as.Date("2022-01-01"), by = "year"),
  A = runif(5, 0.1, 0.4),
  B = runif(5, 0.2, 0.5),
  C = runif(5, 0.3, 0.6)
) %>%
  pivot_longer(cols = -fecha, names_to = "fuente", values_to = "valor")

# Colores arbitrarios sin nombres
colores <- c("#215F53", "#7570B3", "#C7EAE5")

# Gráfico
ggplot(df, aes(x = fecha, y = valor, fill = fuente)) +
  geom_area(position = "stack", color = "white", linewidth = 0.4) +
  scale_fill_manual(values = colores) +
  scale_y_continuous(labels = percent_format()) +
  theme_minimal() +
  theme(
    legend.position = "top",
    legend.title = element_blank()
  )