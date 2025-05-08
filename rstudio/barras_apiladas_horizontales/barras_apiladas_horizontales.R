require(pacman)
pacman::p_load(tidyverse, sf, scales, biscale, cowplot, RColorBrewer, 
               viridis, lubridate, ggtext, readxl, showtext)

# Paleta fija para las categorías
colores <- c(
  "Hombre" = "#4C6A67",
  "Mujer" = "#627B78",
  "No identificado" = "#6F8583"
)
blanco <- "white"

# Tema ATDT
tema_python_atdt <- function() {
  theme_minimal() +
    theme(
      plot.title = element_text(size = 14, face = "bold", color = "black"),
      axis.text = element_text(size = 10, color = "#767676"),
      axis.title = element_text(size = 10, face = "bold", color = "#000000"),
      axis.text.x = element_text(angle = 90, hjust = 1),
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_line(color = "#000000", linewidth = 0.4),
      axis.ticks = element_blank(),
      legend.position = "top",
      plot.background = element_rect(fill = "transparent", color = NA),
      panel.background = element_rect(fill = "transparent", color = NA)
    )
}

# Simular datos apilables
set.seed(123)
fechas <- seq(as.Date("2023-01-01"), as.Date("2023-12-01"), by = "month")
categorias <- c("Hombre", "Mujer", "No identificado")

datos <- expand.grid(fecha = fechas, categoria = categorias) %>%
  mutate(valor = round(runif(n(), 2000, 5000)))

# Gráfica
ggplot(datos, aes(x = fecha, y = valor, fill = categoria)) +
  geom_col(position = "stack", width = 20) +
  scale_fill_manual(values = colores) +
  scale_x_date(
    date_labels = "%b %Y",
    date_breaks = "1 month",
    expand = expansion(mult = c(0.01, 0.01))
  ) +
  scale_y_continuous(
    expand = expansion(mult = c(0, 0.1))
  ) +
  labs(x = "", y = "") +
  tema_python_atdt() +  # primero tu tema base
  theme(                # luego ajustes adicionales
    axis.text.x = element_blank(),
    panel.grid.major.y = element_blank(),
    panel.grid.minor.y = element_blank()
  ) +
  coord_flip()