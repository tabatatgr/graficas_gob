# Librerías
library(tidyverse)
library(scales)
library(lubridate)
library(showtext)
library(openxlsx)

# orientación horizontal o vertical
usar_coord_flip <- FALSE

# Fuente personalizada
font_add_google("Poppins", "Poppins")
showtext_auto()

# Colores
verde_base <- "#10302C"
rojo_maximo <- "#8B0000"
blanco <- "white"

# Simular datos
set.seed(123)
fechas <- seq(as.Date("2023-01-01"), as.Date("2024-12-01"), by = "month")

valores <- c(
  round(rnorm(12, mean = 207.44, sd = 3), 2),
  round(rnorm(12, mean = 248.93, sd = 4), 2)
)
valores[18] <- 300
max_valor <- max(valores)

# Crear datos en formato wide temporalmente
datos_wide <- tibble(
  fecha = fechas,
  total_def = valores
) %>%
  filter(year(fecha) >= 2023) %>%
  mutate(
    color_barra = ifelse(total_def == max_valor, rojo_maximo, verde_base),
    color_badge = color_barra,
    etiqueta = scales::dollar(total_def),
    y_label = total_def + max(total_def) * 0.04
  )

# Convertir a formato long
datos_long <- datos %>%
  pivot_longer(cols = -fecha, names_to = "variable", values_to = "valor", values_transform = list(valor = as.character))

# Separar para graficar: una tabla para barras y otra para etiquetas
datos_barras <- datos_long %>%
  filter(variable == "total_def" | variable == "color_barra")

datos_etiquetas <- datos_wide %>%
  select(fecha, y_label, etiqueta, color_badge)

# Tema
tema_python_atdt <- function() {
  theme_minimal(base_family = "Poppins") +
    theme(
      plot.title = element_text(size = 14, face = "bold", color = "black"),
      axis.text = element_text(size = 10, color = "#767676"),
      axis.title = element_text(size = 10, face = "bold", color = "#000000"),
      axis.text.x = element_text(
        angle = ifelse(usar_coord_flip, 0, 90),
        hjust = ifelse(usar_coord_flip, 0.5, 1),
        vjust = ifelse(usar_coord_flip, 0.5, 1)
      ),
      panel.grid.major.x = if (usar_coord_flip) element_line(color = "#000000", linewidth = 0.4) else element_blank(),
      panel.grid.major.y = if (usar_coord_flip) element_blank() else element_line(color = "#000000", linewidth = 0.4),
      panel.grid.minor = element_blank(),
      axis.ticks = element_blank(),
      legend.position = "none",
      plot.background = element_rect(fill = "transparent", color = NA),
      panel.background = element_rect(fill = "transparent", color = NA)
    )
}

# Gráfico
grafica <- ggplot() +
  geom_col(data = datos_wide, aes(x = fecha, y = total_def, fill = color_barra), width = 20, show.legend = FALSE) +
  geom_label(
    data = datos_etiquetas,
    aes(x = fecha, y = y_label, label = etiqueta, fill = color_badge),
    color = blanco,
    family = "Poppins",
    size = 3.5,
    label.size = 0,
    label.r = unit(6, "pt"),
    show.legend = FALSE,
    angle = ifelse(usar_coord_flip, 0, 90),
    hjust = ifelse(usar_coord_flip, 0.5, 0.1),
    vjust = ifelse(usar_coord_flip, 0.5, 0),
    position = position_nudge(x = 5.5)
  ) +
  scale_fill_identity() +
  scale_x_date(
    date_labels = "%b %Y",
    date_breaks = "1 month",
    expand = expansion(mult = c(0.01, 0.01))
  ) +
  scale_y_continuous(
    labels = dollar_format(),
    expand = expansion(mult = c(0, 0.2))
  ) +
  tema_python_atdt() +
  theme(axis.title.x = element_blank(), axis.title.y = element_blank())

if (usar_coord_flip) {
  grafica <- grafica + coord_flip()
}

# Mostrar y guardar
print(grafica)
ggsave("rstudio/barras/barras.svg", plot = grafica, width = 12, height = 6, dpi = 300)
