#------------------------------------------------------------------------------#
# Proyecto:            Gráfica area plot
#
# Responble: Tabata
# Fecha de creación: 10 de abril de 2025 
# Última actualización:30 de abril de 2025
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------

# Relación:

# 1. Tema - función ATDT
# 2. Leer base de datos
# 3. Ajustar formato de fecha
# 4. Crear gráfica
# 5. Exportar gráfica

#-------------------------------------------------------------------------------
# 00. Configuración inicial ---------------------------------------------------#
#-------------------------------------------------------------------------------

# Librerías 
require(pacman)
pacman::p_load(tidyverse, sf, scales, biscale, cowplot, RColorBrewer, 
               viridis, lubridate, ggtext, readxl, showtext)
# Librerías 
require(pacman)
pacman::p_load(tidyverse, sf, scales, readxl, lubridate, showtext)

# Colores estilo Python
color_area <- "#d4dce9"        # área azul claro
color_linea <- "#2f5597"       # línea principal
color_tendencia <- "#c00000"   # línea punteada roja

# Fuente 
font_add_google("Poppins", "Poppins")
showtext_auto()

# Tema adaptado estilo matplotlib institucional
tema_python_atdt <- function() {
  theme_minimal(base_family = "Poppins") +
    theme(
      plot.title = element_text(size = 14, face = "bold", color = "black"),
      axis.text = element_text(size = 10, color = "#767676"),
      axis.title = element_text(size = 10, face = "bold", color = "#000000"),
      axis.text.x = element_text(angle = 90, hjust = 1),
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_line(color = "#000000", linewidth = 0.4, linetype = "solid"),
      axis.ticks = element_blank(),
      legend.position = "none",
      plot.background = element_rect(fill = "transparent", color = NA),
      panel.background = element_rect(fill = "transparent", color = NA)
    )
}

# Leer datos
datos <- read_excel("/Users/tabatagarcia/Desktop/plantillas/rstudio/datos_graficas/SalarioMinimo.xlsx")
datos$fecha <- as.Date(datos$fecha, format = "%Y-%m-%d")

# Línea de tendencia (modelo lineal)
modelo <- lm(total_def ~ fecha, data = datos)
datos$tendencia <- predict(modelo)

# Crear gráfica
ggplot(datos, aes(x = fecha, y = total_def)) +
  geom_area(fill = color_area, alpha = 1) +
  geom_line(color = color_linea, linewidth = 1.2) +
  geom_line(aes(y = tendencia), color = color_tendencia, linewidth = 1.2, linetype = "dashed") +
  geom_text(
    data = tail(datos, 1),
    aes(label = scales::dollar(total_def)),
    hjust = 0.5, vjust = -1,
    family = "Poppins", size = 4, color = "#10302C"
  ) +
  scale_x_date(date_labels = "%b %Y",
               date_breaks = "1 year")+
  scale_y_continuous(labels = dollar_format(), expand = expansion(mult = c(0.1, 0.15))) +
  labs(
    x = NULL,
    y = NULL
  ) +
  tema_python_atdt()
