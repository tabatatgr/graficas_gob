#------------------------------------------------------------------------------#
# Proyecto:                        Scatter plot
#
# Responble: Tabata
# Fecha de creación: 14 de abril de 2025 
# Última actualización: 30 de abril de 2025
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------


#------------------------------------------------------------------------------#
# 00. Configuración inicial ---------------------------------------------------#
#------------------------------------------------------------------------------#

# Librerías 
require(pacman)
pacman::p_load(tidyverse, sf, scales, biscale, cowplot, RColorBrewer, 
               viridis, lubridate, showtext, ggrepel)

#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#

# Simular datos
set.seed(42)
n <- 50

sim_mun <- tibble(
  cve_municipio = paste("MUN", sprintf("%02d", 1:n)),
  promedio_diario_2023_2024 = runif(n, 0, 15),
  promedio_diario_2024_2025 = promedio_diario_2023_2024 + rnorm(n, 0, 3)
)

sim_mun$cve_municipio[10] <- "CULIACAN"

# Clasificación solo para Culiacán
sim_mun <- sim_mun %>%
  mutate(
    is_culiacan = cve_municipio == "CULIACAN",
    color_cat = ifelse(is_culiacan, "Culiacán", "Normal"),
    alpha_cat = ifelse(is_culiacan, 1, 0.7),
    size_cat = ifelse(is_culiacan, 3.5, 2)
  )

# Límites
lim_min <- min(sim_mun$promedio_diario_2023_2024, sim_mun$promedio_diario_2024_2025)
lim_max <- max(sim_mun$promedio_diario_2023_2024, sim_mun$promedio_diario_2024_2025)

# Colores
colores <- c(
  "Culiacán" = "#671435",
  "Normal"   = "#006157"
)

# Gráfica
graf5 <- ggplot(sim_mun, aes(x = promedio_diario_2023_2024, y = promedio_diario_2024_2025)) +
  geom_abline(slope = 1, intercept = 0, color = "#9D792A", linetype = "dashed") +
  geom_point(aes(color = color_cat, alpha = alpha_cat, size = size_cat), shape = 16) +
  geom_vline(xintercept = 0, color = "gray30", linewidth = 0.4) +
  geom_hline(yintercept = 0, color = "gray30", linewidth = 0.4) +
  geom_text_repel(
    data = sim_mun %>% filter(is_culiacan),  # Solo etiqueta a Culiacán
    aes(label = cve_municipio),
    family = "Poppins", fontface = "bold", size = 3.5,
    box.padding = 0.4, max.overlaps = 10
  ) +
  scale_color_manual(values = colores) +
  scale_alpha_identity() +
  scale_size_identity() +
  scale_x_continuous(limits = c(lim_min, lim_max), labels = comma_format()) +
  scale_y_continuous(limits = c(lim_min, lim_max), labels = comma_format()) +
  tema_estilo_multilinea() +
  theme(
    legend.position = "none",
    plot.margin = margin(10, 10, 10, 10),
      axis.text.x = element_text(angle = 0, vjust = 1, hjust = 1)
  )

# Mostrar
print(graf5)
