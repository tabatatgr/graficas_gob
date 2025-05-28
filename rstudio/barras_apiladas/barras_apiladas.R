# Librerías necesarias
library(tidyverse)
library(scales)
library(lubridate)
library(forcats)

# Activar orientación horizontal (TRUE) o vertical (FALSE)
usar_coord_flip <- FALSE

# Establecer idioma español para meses
Sys.setlocale("LC_TIME", "es_ES.UTF-8")  # Mac/Linux
# Sys.setlocale("LC_TIME", "Spanish")    # Windows 

# Colores estilo Python
colores <- c(
  "Hombre" = "#4C6A67",
  "Mujer" = "#627B78",
  "No identificado" = "#6F8583"
)

# Simular datos
set.seed(123)
fechas <- seq(as.Date("2023-01-01"), as.Date("2023-12-01"), by = "month")
categorias <- c("Hombre", "Mujer", "No identificado")

datos <- expand.grid(fecha = fechas, categoria = categorias) %>%
  mutate(valor = round(runif(n(), 2000, 5000))) %>%
  group_by(fecha) %>%
  mutate(
    total_mes = sum(valor),
    pct = valor / total_mes * 100
  ) %>%
  ungroup() %>%
  mutate(
    mes = format(fecha, "%B %Y") |> str_to_title(),
    etiqueta_pct = paste0(round(pct, 1), "%"),
    mes = fct_rev(factor(mes))
  )

# Totales por mes
totales <- datos %>%
  group_by(mes) %>%
  summarise(total = sum(valor), .groups = "drop") %>%
  mutate(pct_general = total / sum(total) * 100)

datos <- datos %>% left_join(totales, by = "mes")

# Ajuste dinámico de etiquetas según orientación
if (usar_coord_flip) {
  ajuste_capsula <- list(hjust = -0.1)
  ajuste_pct <- list(hjust = 0)
  theme_ejes <- theme(
    panel.grid.major.x = element_line(color = "#B9B9B9"),
    panel.grid.major.y = element_blank()
  )
} else {
  ajuste_capsula <- list(vjust = -0.3)
  ajuste_pct <- list(vjust = 0)
  theme_ejes <- theme(
    panel.grid.major.y = element_line(color = "#B9B9B9"),
    panel.grid.major.x = element_blank()
  )
}

# Crear gráfico base
grafica <- ggplot() +
  geom_col(
    data = datos,
    aes(x = mes, y = valor, fill = categoria),
    position = position_stack(reverse = TRUE),
    width = 0.7
  ) +
  geom_text(
    data = datos,
    aes(x = mes, y = valor, label = etiqueta_pct),
    position = position_stack(vjust = 0.5, reverse = TRUE),
    color = "white",
    size = 3.5,
    fontface = "bold"
  ) +
  # Cápsula de total (ajuste automático según orientación)
  do.call(geom_label, c(
    list(
      data = totales,
      mapping = aes(x = mes, y = total, label = scales::comma(total)),
      size = 4,
      label.size = 0.3,
      fill = "white",
      color = "#10302C",
      label.r = unit(0.5, "lines"),
      fontface = "bold"
    ),
    ajuste_capsula
  )) +
  # Porcentaje general (ajuste automático)
  do.call(geom_text, c(
    list(
      data = totales,
      mapping = aes(x = mes, y = total + max(total) * 0.1,
                    label = paste0(round(pct_general, 1), "%")),
      size = 4,
      color = "#4C6A67",
      fontface = "bold"
    ),
    ajuste_pct
  )) +
  scale_fill_manual(values = colores) +
  scale_y_continuous(labels = comma, expand = expansion(mult = c(0, 0.15))) +
  labs(x = NULL, y = NULL, fill = NULL) +
  theme_minimal(base_size = 12) +
  theme(
    axis.text.y = element_text(face = "bold"),
    axis.text.x = element_text(size = 10, color = "#767676", angle = 45, hjust = 1, vjust = 1),
    legend.text = element_text(size = 10),
    plot.background = element_rect(fill = "white", color = NA),
    panel.background = element_rect(fill = "white", color = NA)
  ) +
  theme_ejes

# Agregar coord_flip si aplica
if (usar_coord_flip) {
  grafica <- grafica + coord_flip()
}

# Mostrar gráfico
print(grafica)


# Guardar el gráfico
ggsave("rstudio/barras_apiladas/barras_apiladas.svg", plot = grafica, width = 12, height = 6, dpi = 300)