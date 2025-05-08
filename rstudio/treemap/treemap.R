#------------------------------------------------------------------------------#
# Proyecto:                        Tree Map
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
               viridis, lubridate, showtext, treemapify)

#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#
#------------------------------------------------------------------------------#

# Fuente 
font_add_google("Poppins", "Poppins")
showtext_auto()

# Datos simulados
data <- tibble::tibble(
  entidad = c("CDMX", "Jalisco", "Edomex", "Nuevo León", "Chiapas", "Yucatán", "Sonora"),
  total = c(20000, 18000, 17000, 16000, 9000, 6000, 4000)
)

# Porcentaje
data <- data %>%
  arrange(desc(total)) %>%
  mutate(
    porcentaje = round(total / sum(total) * 100, 1),
    etiqueta = paste0(entidad, "\n", format(total, big.mark = ","), "\n", porcentaje, "%")
  )

# Colores
verde_oscuro <- "#10302C"
verde_claro <- "#4C6A67"
data <- data %>%
  mutate(
    color = ifelse(total == max(total), verde_oscuro, verde_claro)
  )

# Treemap
ggplot(data, aes(area = total, fill = color, label = etiqueta)) +
  geom_treemap(color = "white", linewidth = 3) +
  geom_treemap_text(
    family = "Poppins", fontface = "bold", colour = "white",
    place = "topleft", grow = FALSE, reflow = TRUE, 
    lineheight = 1.1, size = 7
  ) +
  scale_fill_identity() +
  theme_void()