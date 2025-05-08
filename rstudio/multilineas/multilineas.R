#------------------------------------------------------------------------------#
# Proyecto:                       Líneas
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

### Paleta de color
# Colores estilo limpio
verde_base <- "#10302C"
rojo_maximo <- "#8B0000"
blanco <- "white"
azul_linea <- "#2F5597"
naranja_linea <- "#D55E00"

# - > Colores categóricos
# Al gráficar datos que comparen países u otros sectores se utilizarán estos 
# degradados. (En caso de requerir colores adiciones, se solicitan a diseño)

categoricos <- c("#018477","#00AF9D","#5E000E","#830B1A","#59c959","#ACE5AC",
                 "#BD0000","#C51228","#FFC0CC","#FF6666","#00008B","#3939C4",
                 "#65087C", "#854991")

#------------------------------------------------------------------------------#
# 01. Lineal ------------------------------------------------------------------#
#------------------------------------------------------------------------------#

library(legendry)
library(ggh4x) # para poner doble línea en el eje x

set.seed(001)  # seed

# Generamos observaciones con exactamente 12 meses por año
df5 <- data.frame(
  Fecha = seq(as.Date("2018-01-01"), as.Date("2025-03-01"), by = "1 month"),
  y = round(runif(87, min = 10000, max = 20000), 2)  # Valores aleatorios entre 10,000 y 20,000
)

ultimo_punto5 <- df5 %>% slice_tail(n = 1)

# Fuente local
font_add("Poppins", "~/Desktop/plantillas/python/agrupadasyapiladas/fonts/poppins/Poppins-Regular.ttf")
showtext_auto()

# Tema visual tipo matplotlib limpio
tema_estilo_multilinea <- function() {
  theme_minimal(base_family = "Poppins") +
    theme(
      plot.title = element_text(size = 14, face = "bold", color = "black"),
      axis.text = element_text(size = 10, color = "#4D4D4D"),
      axis.title = element_blank(),
      axis.text.x = element_text(angle = 90, hjust = 1),
      panel.grid.major = element_line(color = "#E5E5E5", linewidth = 0.3),
      panel.grid.minor = element_blank(),
      panel.background = element_rect(fill = "white", color = NA),
      plot.background = element_rect(fill = "white", color = NA),
      legend.position = "top",
      legend.title = element_blank(),
      legend.text = element_text(size = 10),
      axis.ticks = element_blank()
    )
}

# Base de datos
datos <- read_excel("~/Desktop/plantillas/rstudio/datos_graficas/SalarioMinimo.xlsx")
datos$fecha <- as.Date(datos$fecha)
datos <- datos %>% filter(year(fecha) >= 2023)

# Modelo de tendencia
modelo <- lm(total_def ~ fecha, data = datos)
datos$tendencia <- predict(modelo)

# Gráfica
grafica <- ggplot(datos, aes(x = fecha)) +
  geom_line(aes(y = total_def, color = "Observado"), linewidth = 1) +
  geom_line(aes(y = tendencia, color = "Tendencia"), linewidth = 1.2, linetype = "dashed") +
  geom_hline(yintercept = 0, color = "gray30", linewidth = 0.4) +
  scale_color_manual(values = c("Observado" = azul_linea, "Tendencia" = rojo_maximo)) +
  scale_x_date(date_labels = "%b %Y", date_breaks = "1 month", expand = expansion(mult = c(0.01, 0.01))) +
  scale_y_continuous(labels = dollar_format()) +
  tema_estilo_multilinea()

# Mostrar
print(grafica)

#------------------------------------------------------------------------------#
# 02. Multilineal -------------------------------------------------------------#
#------------------------------------------------------------------------------#

# Colores y tema
colores <- c("#006157", "#767676", "#671435", "#9B2247")
blanco <- "white"

set.seed(123)
fechas <- seq(as.Date("2000-12-31"), as.Date("2025-12-31"), by = "year")
n <- length(fechas)

df <- tibble(
  Fecha = fechas,
  Trigo = c(sort(runif(n - 5, 100, 4000)), runif(5, 500, 1000)),
  Maiz = c(sort(runif(n - 5, 100, 3500)), runif(5, 400, 800)),
  Frijol = c(sort(runif(n - 5, 100, 3000)), runif(5, 300, 700)),
  Soja = c(sort(runif(n - 5, 100, 2500)), runif(5, 100, 500))
)

# Transformar a formato largo
df_largo <- df %>%
  pivot_longer(cols = -Fecha, names_to = "variable", values_to = "valor")

# Últimos puntos para badge
etiquetas <- df_largo %>%
  group_by(variable) %>%
  filter(Fecha == max(Fecha)) %>%
  mutate(etiqueta = scales::dollar(valor))

# Crear badges bien distribuidos verticalmente
etiquetas <- df_largo %>%
  group_by(variable) %>%
  filter(Fecha == max(Fecha)) %>%
  ungroup() %>%
  arrange(desc(valor)) %>%  # ordenar globalmente por valor
  mutate(
    etiqueta = scales::dollar(valor),
    x_label = Fecha + lubridate::days(30),         # desplazar a la derecha
    y_label = valor + row_number() * -250           # separar verticalmente
  )

# Gráfica
ggplot(df_largo, aes(x = Fecha, y = valor, color = variable)) +
  geom_line(linewidth = 1) +
  geom_hline(yintercept = 0, color = "gray30", linewidth = 0.4) +
  scale_color_manual(values = colores) +
  geom_label(data = etiquetas,
             aes(x = x_label, y = y_label, label = etiqueta, fill = variable),
             color = blanco,
             family = "Poppins",
             size = 3.5,
             label.size = 0,
             label.r = unit(6, "pt"),
             hjust = 0.6,
             vjust = -4,
             show.legend = FALSE) +
  scale_fill_manual(values = colores) +
  scale_y_continuous(labels = scales::dollar_format()) +
  scale_x_date(date_labels = "%Y", date_breaks = "2 year") +
  tema_estilo_multilinea() +
  theme(axis.title.x = element_blank(), axis.title.y = element_blank())


