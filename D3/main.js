// Este script carga los datos y llama a la función del gráfico.

async function init() {
    // Carga tus datos. D3 puede cargar CSV, JSON, etc.
    // Asumimos que tu DataFrame se ha guardado como un CSV.
    const data = await d3.csv("datos.csv");

    // --- CONFIGURACIÓN (Equivalente a los parámetros de tu función Python) ---
    const config = {
        // --- DATOS Y ESTRUCTURA ---
        // 'data' se pasa por separado.
        // La lógica de 'agregar_datos' y 'unir_barras' se haría aquí, en la preparación de datos.
        columnasLineas: ["Mi Linea"], // Lista de columnas que serán líneas
        
        // --- GRÁFICA GENERAL ---
        nombre: "grafico_d3",
        tipoLetra: 'Montserrat',
        anchoFig: 1200,
        altoFig: 600,
        grillas: true,

        // --- BARRAS ---
        anchoBarra: 0.85, // Se usa como padding en la escala de D3
        paletaColores: ["#10302C", "#4C6A67", "#8FA8A6", "#A3C9A8"],
        
        // --- TEXTOS EN BARRAS ---
        valorBarra: true,
        porceBarra: true,
        porceAbajo: true,
        tamLetraValorBarra: 14,
        weightValorBarra: 'bold',
        tamLetraPorceBarra: 11,
        weightPorceBarra: 'bold',

        // --- CÁPSULAS ---
        valorCapsu: true,
        tamLetraValorCapsu: 14,
        weightValorCapsu: 'bold',
        colorBordeCapsu: '#002F2A',
        weightBordeCapsu: 1.5,

        // --- LEYENDA ---
        leyenda: "Categorías Principales",
        posLeyenda: 'arriba',
        
        // --- EJES ---
        tamLetraEjeX: 12,
        weightLetraEjeX: 'medium',
        nombreEjeY: "Valor Total",
        tamLetraNombreEjeY: 14,
        // ... y así sucesivamente para cada parámetro que quieras controlar.
    };

    // Llama a la función del gráfico, pasándole el contenedor, los datos y la configuración.
    verticalBarChart("#chart-container", data, config);
}

init();