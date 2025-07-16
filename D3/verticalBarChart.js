function verticalBarChart(container, data, config) {
    // --- 1. CONFIGURACIÓN INICIAL Y MÁRGENES ---
    const cfg = { ...config }; // Copia de la configuración
    const margin = { top: 80, right: 50, bottom: 100, left: 60 };
    const width = cfg.anchoFig - margin.left - margin.right;
    const height = cfg.altoFig - margin.top - margin.bottom;

    // Limpia el contenedor por si se redibuja
    d3.select(container).html('');

    // Crea el lienzo SVG
    const svg = d3.select(container)
        .append("svg")
        .attr("width", width + margin.left + margin.right)
        .attr("height", height + margin.top + margin.bottom)
        .append("g")
        .attr("transform", `translate(${margin.left},${margin.top})`);

    // --- 2. PREPARACIÓN DE DATOS (Equivalente a tus secciones 2, 3, 4) ---
    // D3 espera que los datos numéricos sean números, no strings.
    data.forEach(d => {
        for (let key in d) {
            if (key !== 'Entidad') d[key] = +d[key]; // 'Entidad' es la categoría del eje X
        }
    });

    const columnasBarras = Object.keys(data[0]).filter(k => k !== 'Entidad' && !cfg.columnasLineas.includes(k));
    
    // Apilado de datos: D3 hace esto automáticamente.
    const stack = d3.stack().keys(columnasBarras);
    const stackedData = stack(data);

    // --- 3. ESCALAS (Equivalente a tus cálculos de límites de ejes) ---
    const xScale = d3.scaleBand()
        .domain(data.map(d => d.Entidad))
        .range([0, width])
        .padding(1 - cfg.anchoBarra);

    const yDomain = [
        d3.min(stackedData, layer => d3.min(layer, d => d[0])), // Mínimo de los valores negativos
        d3.max(stackedData, layer => d3.max(layer, d => d[1]))  // Máximo de los valores positivos
    ];
    const yScale = d3.scaleLinear()
        .domain(yDomain)
        .range([height, 0]);

    const colorScale = d3.scaleOrdinal()
        .domain(columnasBarras)
        .range(cfg.paletaColores);

    // --- 4. EJES Y GRILLAS ---
    const xAxis = d3.axisBottom(xScale);
    svg.append("g")
        .attr("class", "axis axis-x")
        .attr("transform", `translate(0,${yScale(0)})`) // Posiciona el eje X en el cero
        .call(xAxis)
        .selectAll("text")
        .style("font-size", `${cfg.tamLetraEjeX}px`)
        .style("font-weight", cfg.weightLetraEjeX)
        .attr("transform", "rotate(-90)")
        .attr("text-anchor", "end")
        .attr("dx", "-.8em")
        .attr("dy", ".15em");

    const yAxis = d3.axisLeft(yScale);
    svg.append("g")
        .attr("class", "axis axis-y")
        .call(yAxis);
    
    if (cfg.grillas) {
        svg.append("g")
            .attr("class", "grid")
            .call(d3.axisLeft(yScale).tickSize(-width).tickFormat(""));
    }

    // --- 5. DIBUJO DE BARRAS (Equivalente a tu bucle principal) ---
    // El patrón Enter-Update-Exit de D3 reemplaza tu bucle `for`.
    const barGroups = svg.selectAll(".bar-group")
        .data(stackedData)
        .enter().append("g")
        .attr("class", "bar-group")
        .attr("fill", d => colorScale(d.key));

    barGroups.selectAll("rect")
        .data(d => d)
        .enter().append("rect")
        .attr("x", d => xScale(d.data.Entidad))
        .attr("y", d => yScale(d[1]))
        .attr("height", d => yScale(d[0]) - yScale(d[1]))
        .attr("width", xScale.bandwidth())
        // Aquí se replicaría tu lógica de personalización de bordes
        .attr("stroke", cfg.colorBordeBarra || "none")
        .attr("stroke-width", cfg.grosorBordeBarra || 0);

    // --- 6. TEXTOS Y CÁPSULAS (El núcleo de la solución) ---
    // D3 te da las herramientas para implementar cualquier lógica de posicionamiento.
    
    // TEXTO DENTRO DE LAS BARRAS
    if (cfg.valorBarra || cfg.porceBarra) {
        barGroups.selectAll(".bar-text")
            .data(d => d)
            .enter()
            .append("text")
            .attr("class", "bar-text")
            .attr("x", d => xScale(d.data.Entidad) + xScale.bandwidth() / 2)
            .attr("y", d => yScale(d[1]) + (yScale(d[0]) - yScale(d[1])) / 2)
            .attr("text-anchor", "middle")
            .attr("fill", "#fff") // Aquí iría tu lógica `get_text_color_for_bg`
            .style("font-size", `${cfg.tamLetraValorBarra}px`)
            .style("font-weight", cfg.weightValorBarra)
            .text(d => {
                const value = d[1] - d[0];
                return d3.format(",.0f")(value); // Formatea el número
            });
        // La lógica para `porceAbajo` implicaría añadir un segundo elemento <text> con un `dy` diferente.
    }

    // CÁPSULAS SOBRE LAS BARRAS
    if (cfg.valorCapsu) {
        const totalData = data.map(d => {
            const total = d3.sum(columnasBarras, k => d[k]);
            return { Entidad: d.Entidad, Total: total };
        });

        svg.selectAll(".capsule-text")
            .data(totalData)
            .enter()
            .append("text")
            .attr("class", "capsule-text")
            .attr("x", d => xScale(d.Entidad) + xScale.bandwidth() / 2)
            .attr("y", d => yScale(d.Total) - 10) // 10px de padding
            .attr("text-anchor", "middle")
            .style("font-size", `${cfg.tamLetraValorCapsu}px`)
            .style("font-weight", cfg.weightValorCapsu)
            .text(d => d3.format(",.0f")(d.Total))
            // Para la cápsula con borde, en lugar de un `bbox` de Matplotlib,
            // se dibuja un <rect> detrás del texto.
            .clone(true).lower() // Clona el texto, lo pone detrás
            .attr("stroke", cfg.colorBordeCapsu)
            .attr("stroke-width", cfg.weightBordeCapsu)
            .attr("stroke-linejoin", "round");
    }
    
    // --- 7. LEYENDA ---
    if (cfg.leyenda) {
        const legend = svg.append("g")
            .attr("transform", `translate(0, ${-margin.top / 2})`); // Posición arriba

        const legendItems = legend.selectAll(".legend-item")
            .data(columnasBarras)
            .enter().append("g")
            .attr("class", "legend-item")
            .attr("transform", (d, i) => `translate(${i * 100}, 0)`); // Espaciado simple

        legendItems.append("rect")
            .attr("width", 15)
            .attr("height", 15)
            .attr("fill", d => colorScale(d));

        legendItems.append("text")
            .attr("x", 20)
            .attr("y", 12)
            .text(d => d);
    }
    
    // --- 8. GUARDADO (Manejado externamente) ---
    // D3 no guarda archivos directamente. Se usaría una biblioteca como `svg-crowbar`
    // o se configuraría un botón en el HTML para descargar el SVG.
    // La conversión a PNG se haría en el servidor con una herramienta como `puppeteer`.
}