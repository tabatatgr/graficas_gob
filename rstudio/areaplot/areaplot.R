library(tidyverse)
library(scales)
library(ggtext)
library(showtext)
library(sysfonts)

# Fuente Poppins desde Google
font_add_google("Poppins", "Poppins")
showtext_auto()

# Simulación de datos
set.seed(1)
df <- tibble(
  fecha = seq(as.Date("2018-01-01"), as.Date("2022-01-01"), by = "year"),
  comisiones = runif(5, 0.1, 0.4),
  fiscalias = runif(5, 0.2, 0.5),
  portal = runif(5, 0.3, 0.6)
) %>%
  pivot_longer(cols = -fecha, names_to = "fuente", values_to = "valor") %>%
  group_by(fecha) %>%
  mutate(pct = valor / sum(valor)) %>%
  ungroup()

# Paleta de colores
colores <- c(
  "comisiones" = "#215F53",
  "fiscalias" = "#7570B3",
  "portal"     = "#C7EAE5"
)

# Etiquetas centradas: valor promedio de cada área por fecha
etiquetas <- df %>%
  group_by(fuente) %>%
  summarise(pct = mean(pct), fecha = median(fecha), .groups = "drop")

# Tema personalizado
tema_area_custom <- theme_minimal(base_family = "Poppins") +
  theme(
    panel.grid.major.x = element_blank(),
    panel.grid.major.y = element_line(color = "white", size = 1),
    panel.grid.minor = element_blank(),
    panel.background = element_rect(fill = "#F9F9F9", color = NA),
    plot.background = element_rect(fill = "#F9F9F9", color = NA),
    axis.title = element_blank(),
    axis.text.x = element_text(size = 24, color = "#767676", face = "bold", angle = 90, hjust = 1),
    axis.text.y = element_text(size = 24, color = "#767676", face = "bold"),
    legend.position = "top",
    legend.title = element_blank(),
    legend.text = element_text(family = "Poppins", size = 20, color = "#767676", face = "bold")
  )

# Calcular promedios de porcentaje por fuente
porcentajes <- df %>%
  group_by(fuente) %>%
  summarise(pct_promedio = mean(pct)) %>%
  mutate(
    color = colores[fuente],  # Asignar el color correspondiente
    pct_formateado = scales::percent(pct_promedio, accuracy = 0.1)
  )

# Imprimir resultados
print(porcentajes)

# Gráfico
grafica <- ggplot(df, aes(x = fecha, y = pct, fill = fuente)) +
  geom_area(position = "stack", color = "white", linewidth = 0.3) +
  scale_fill_manual(values = colores) +
  scale_y_continuous(labels = percent_format(accuracy = 1)) +
  scale_x_date(date_labels = "%b %Y", date_breaks = "1 year") +
  labs() +
  tema_area_custom

# Mostrar
print(grafica)

# Guardar
ggsave("rstudio/areaplot/areaplot.svg", plot = grafica, width = 12, height = 6, dpi = 300)
ggsave("rstudio/areaplot/areaplot.png", plot = grafica, width = 12, height = 6, dpi = 300)
