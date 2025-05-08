library(tidyverse)
library(lubridate)
library(ggplot2)
library(svglite)
library(systemfonts)

# Crear fechas mensuales
fecha <- seq(as.Date("2010-01-01"), as.Date("2025-01-01"), by = "months")

# Crear datos de ejemplo para cada indicador
datos_con <- tibble(
  fecha = fecha,
  indicador = "Con datos",
  valor = round(runif(length(fecha), 50, 200)),
  estado = "Jalisco"
)

datos_sin <- tibble(
  fecha = fecha,
  indicador = "Sin datos",
  valor = round(runif(length(fecha), 10, 100)),
  estado = "Jalisco"
)

# Unir ambos
datos <- bind_rows(datos_con, datos_sin)

# Crear variable de mes
datos <- datos %>%
  mutate(mes = floor_date(fecha, "month"))

# Resumir por mes e indicador
datos_sum <- datos %>%
  group_by(mes, indicador) %>%
  summarise(valor = sum(valor), .groups = "drop")

# Tema personalizado
theme_personalizado <- theme_minimal(base_size = 12) +
  theme(
    plot.title = element_text(face = "bold"),
    axis.text.x = element_text(angle = 90, hjust = 1, size = 6),
    axis.text.y = element_text(size = 6),
    axis.title = element_text(size = 10),
    panel.border = element_rect(color = "gray20", fill = NA, linewidth = 0.5),
    axis.ticks = element_blank(),
    panel.grid = element_blank(),
    legend.position = "right"
  )

# Crear gráfica
grafica <- ggplot(datos_sum, aes(x = mes, y = valor, fill = indicador)) +
  geom_col(position = "stack", width = 30) +
  scale_fill_manual(values = c("Con datos" = "#584290", "Sin datos" = "#b1adcf")) +
  labs(
    title = "Ejemplo de gráfica de barras apiladas",
    x = "Fecha",
    y = "Número de casos",
    fill = NULL
  ) +
  scale_x_date(date_breaks = "2 years", date_labels = "%Y") +
  theme_personalizado

grafica

# Crear carpeta
dir.create("~/Desktop/plantillas/rstudio/barras_tendencias", recursive = TRUE, showWarnings = FALSE)

# Guardar archivos
ggsave("~/Desktop/plantillas/rstudio/barras_tendencias/barras_tendencias.png",
       plot = grafica, width = 10, height = 5, dpi = 300)

ggsave("~/Desktop/plantillas/rstudio/barras_tendencias/barras_tendencias.svg",
       plot = grafica, width = 10, height = 5, dpi = 300)
