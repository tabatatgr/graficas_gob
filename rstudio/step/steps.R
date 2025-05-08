#------------------------------------------------------------------------------#
# Proyecto:                       Steps
#
# Responble: Tabata
# Fecha de creación: 3 de abril de 2025 
# Última actualización: 30 de abril de 2025
#------------------------------------------------------------------------------#
#-------------------------------------------------------------------------------


#------------------------------------------------------------------------------#
# 00. Configuración inicial ---------------------------------------------------#
#------------------------------------------------------------------------------#

# Librerías 
require(pacman)
pacman::p_load(tidyverse, sf, scales, biscale, cowplot, RColorBrewer, 
               viridis, lubridate, showtext)
# Librerías
require(pacman)
pacman::p_load(tidyverse, lubridate, showtext, scales)

# Fuente y estilo
font_add("Poppins", "/Users/tabatagarcia/Desktop/plantillas/python/agrupadasyapiladas/fonts/poppins/Poppins-Regular.ttf")
showtext_auto()

# Tema limpio tipo matplotlib
tema_python_atdt_2 <- function() {
  theme_minimal(base_family = "Poppins") +
    theme(
      plot.title = element_text(size = 20, face = "bold", color = "black"),
      axis.text = element_text(size = 14, color = "#767676"),
      axis.title = element_blank(),
      panel.grid.major.x = element_blank(),
      panel.grid.minor = element_blank(),
      panel.grid.major.y = element_line(color = "#000000", linewidth = 0.4),
      axis.ticks = element_blank(),
      plot.background = element_rect(fill = "transparent", color = NA),
      panel.background = element_rect(fill = "transparent", color = NA)
    )
}

# Datos simulados
set.seed(123)
df <- data.frame(
  Fecha = seq(as.Date("2023-01-01"), as.Date("2024-12-01"), by = "1 month"),
  y = round(runif(24, min = 50, max = 200), 2)
)

# Último punto
ultimo_punto <- df %>% slice_tail(n = 1)
max_valor <- max(df$y, na.rm = TRUE)
min_valor <- min(df$y, na.rm = TRUE)

# Gráfica
ggplot(df, aes(x = Fecha, y = y)) + 
  geom_step(color = "#691c32", linewidth = 1.4, direction = "mid") +
  geom_point(color = "#691c32", size = 3) +
  geom_vline(xintercept = 0, color = "gray30", linewidth = 0.4) +       # línea eje Y
  geom_hline(yintercept = 0, color = "gray30", linewidth = 0.4) +       # línea eje X
  geom_vline(xintercept = as.Date("2024-10-01"), color = "#BC955C", 
             linetype = "dashed", linewidth = 1.1) +  
  geom_text(
    data = ultimo_punto,
    aes(label = scales::comma(y)),
    vjust = -1,
    fontface = "bold",
    size = 5,
    family = "Poppins"
  ) +
  scale_y_continuous(labels = comma_format(),
                     expand = expansion(mult = c(0, 0.3))) +
  scale_x_date(date_breaks = "1 month", date_labels = "%b") +
  tema_python_atdt_2() +
  theme(
    axis.text.x = element_text(angle = 45, hjust = 1)
  )