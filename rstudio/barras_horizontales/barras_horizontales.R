#------------------------------------------------------------------------------#
# Proyecto:            Gráfica de barras vertical para $
#
# Responble: Tabata
# Fecha de creación: 3 de abril de 2025 
# Última actualización: 30 de abril de 2025
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

# Paleta de color
verde_base <- "#10302C"
rojo_maximo <- "#8B0000"
blanco <- "white"

#fonts
font_add("Poppins", "/Users/tabatagarcia/Desktop/plantillas/python/agrupadasyapiladas/fonts/poppins/Poppins-Regular.ttf")
showtext_auto()

# Activa showtext
showtext_auto()

# Tema-función ATDT 

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

#-------------------------------------------------------------------------------
# 01. Base de datos -----------------------------------------------------------#
#-------------------------------------------------------------------------------

datos <- read_excel("~/Desktop/plantillas/rstudio/datos_graficas/SalarioMinimo.xlsx")

# Ajustar formato de fecha
datos$fecha <- as.Date(datos$fecha, format = "%Y-%m-%d")

datos <- datos %>% filter(lubridate::year(fecha) >= 2023)

# Columna valor max
max_valor <- max(datos$total_def, na.rm = TRUE)
datos <- datos %>%
  mutate(
    color_badge = ifelse(total_def == max_valor, rojo_maximo, verde_base),
    etiqueta = scales::dollar(total_def)
  )

datos <- datos %>%
  mutate(
    color_barra = ifelse(total_def == max_valor, rojo_maximo, verde_base),
    color_badge = color_barra,
    etiqueta = scales::dollar(total_def)
  )

datos <- datos %>%
  mutate(
    color_barra = ifelse(total_def == max(total_def, na.rm = TRUE), rojo_maximo, verde_base),
    color_badge = color_barra,
    etiqueta = scales::dollar(total_def),
    y_label = total_def + max(total_def) * 0.3 
  )

grafica <- ggplot(datos, aes(x = fecha, y = total_def)) +
  geom_col(aes(fill = color_barra), width = 20, show.legend = FALSE) +
  geom_label(aes(y = y_label, label = etiqueta, fill = color_badge),
             color = blanco,
             family = "Poppins",
             size = 3.5,
             label.size = 0,
             angle = 0,    
             label.r = unit(6, "pt"),
             hjust = 1,         
             vjust = 0.45,  
             show.legend = FALSE) +
  scale_fill_identity() +
  scale_x_date(
    date_labels = "%b %Y",
    date_breaks = "1 month",
    expand = expansion(mult = c(0.01, 0.01))
  ) +
  scale_y_continuous(
    labels = scales::dollar_format(),
    expand = expansion(mult = c(0, 0.2))
  ) +
  tema_python_atdt() +
  theme(axis.title.x = element_blank(), axis.title.y = element_blank(),
        axis.text.x = element_blank(),
        panel.grid.major.y = element_blank()) +
  coord_flip()

# Mostrar
print(grafica)
