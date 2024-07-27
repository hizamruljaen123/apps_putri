document.addEventListener('DOMContentLoaded', function() {
    // Toggle sidebar visibility
    function toggleSidebar() {
        var sidebar = document.getElementById('sidebar');
        sidebar.classList.toggle('hidden');
    }

    // Show loading screen
    function showLoading() {
        const loadingScreen = document.createElement('div');
        loadingScreen.id = 'loading-screen';
        loadingScreen.className = 'fixed inset-0 flex items-center justify-center bg-gray-900 bg-opacity-50 z-50';
        loadingScreen.innerHTML = '<div class="spinner-border animate-spin inline-block w-8 h-8 border-4 rounded-full text-white" role="status"></div>';
        document.body.appendChild(loadingScreen);
    }

    // Hide loading screen
    function hideLoading() {
        const loadingScreen = document.getElementById('loading-screen');
        if (loadingScreen) {
            loadingScreen.remove();
        }
    }

    // Show alert
    function showAlert(type, message) {
        const alertDiv = document.createElement('div');
        alertDiv.className = `fixed top-4 left-1/2 transform -translate-x-1/2 p-4 mb-4 text-sm rounded-lg ${
            type === 'success' ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
        }`;
        alertDiv.innerHTML = message;

        document.body.appendChild(alertDiv);
        
        setTimeout(() => {
            alertDiv.remove();
        }, 3000);
    }

    // Submit data function
    function submitData(event) {
        event.preventDefault();

        // Show loading screen
        showLoading();

        setTimeout(() => {
            const dataSpec = {
                Merek: document.getElementById('merek').value,
                Tipe: document.getElementById('tipe').value,
                Kamera_Utama_MP: document.getElementById('kamera-utama').value,
                Kamera_Depan_MP: document.getElementById('kamera-depan').value,
                RAM: document.getElementById('ram').value,
                Memori_Internal: document.getElementById('memori-internal').value,
                Baterai_mAh: document.getElementById('baterai').value,
                Jenis_Layar: document.getElementById('jenis-layar').value
            };

            const dataPenjualan = {
                Jumlah_Penjualan: document.getElementById('jumlah-penjualan').value,
                Total_Penjualan: document.getElementById('total-penjualan').value
            };

            // Send the data to the server
            fetch('/submit-data', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ dataSpec, dataPenjualan })
            })
            .then(response => response.json())
            .then(result => {
                // Hide loading screen
                hideLoading();

                if (result.status === 'success') {
                    showAlert('success', 'Data successfully submitted!');
                } else {
                    showAlert('error', `Error: ${result.message}`);
                }
                // Close the modal or handle success
                document.getElementById('input-modal').classList.add('hidden');
            })
            .catch(error => {
                // Hide loading screen
                hideLoading();
                showAlert('error', `Error: ${error.message}`);
            });
        }, 2000); // Delay for 2 seconds
    }

    // Attach the submit handler to the form
    document.getElementById('form-data').addEventListener('submit', submitData);

    // Fetch data and display in table
    async function fetchDataAndDisplay() {
        try {
            let response = await fetch('/perform-clustering', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({ "threshold": 0.3 }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            let data = await response.json();
            let tableBody = document.getElementById('data-table-cluster');

            tableBody.innerHTML = ''; // Clear existing table data

            // Sort data by Cluster
            data.data.sort((a, b) => a.Cluster - b.Cluster);

            // Append rows to the table
            data.data.forEach((item, index) => {
                let row = `
                    <tr class="border-b border-gray-200 hover:bg-gray-100">
                        <td class="py-3 px-6 text-left">${index + 1}</td>
                        <td class="py-3 px-6 text-left">${item.Cluster}</td>
                        <td class="py-3 px-6 text-left">${item.Kategori_Penjualan}</td>
                        <td class="py-3 px-6 text-left">${item.Bulan}</td>
                        <td class="py-3 px-6 text-left">${item.Merek}</td>
                        <td class="py-3 px-6 text-left">${item.Persentase_Jumlah_Terjual.toFixed(4)}%</td>
                        <td class="py-3 px-6 text-left">${item.Tipe}</td>
                    </tr>
                `;
                tableBody.innerHTML += row;
            });

            // Count unique values for Card 1
            let uniqueMerek = new Set();
            let uniqueTipe = new Set();
            let uniqueBulan = new Set();
            let uniqueCluster = new Set();

            data.data.forEach(item => {
                uniqueMerek.add(item.Merek);
                uniqueTipe.add(item.Tipe);
                uniqueBulan.add(item.Bulan);
                uniqueCluster.add(item.Cluster);
            });

            document.getElementById('unique-merek').textContent = uniqueMerek.size;
            document.getElementById('unique-tipe').textContent = uniqueTipe.size;
            document.getElementById('unique-bulan').textContent = uniqueBulan.size;
            document.getElementById('unique-cluster').textContent = uniqueCluster.size;

            // Count categories for Card 2
            let categoryCounts = {
                'Sangat Rendah': 0,
                'Rendah': 0,
                'Cukup': 0,
                'Berpotensi Tinggi': 0,
                'Tinggi': 0,
                'Sangat Tinggi': 0
            };

            data.data.forEach(item => {
                categoryCounts[item.Kategori_Penjualan]++;
            });

            // Create summary table for Card 2
            let summaryTableBody = document.getElementById('summary-table-body');
            summaryTableBody.innerHTML = '';

            for (let category in categoryCounts) {
                let summaryRow = `
                    <tr class="border-b border-gray-200 hover:bg-gray-100">
                        <td class="py-3 px-6 text-left">${category}</td>
                        <td class="py-3 px-6 text-left">${categoryCounts[category]}</td>
                    </tr>
                `;
                summaryTableBody.innerHTML += summaryRow;
            }
        } catch (error) {
            console.error('Error fetching data:', error);
        }
    }

    // Fetch and format sales data
    async function fetchSalesData(tabId, tableId) {
        try {
            const response = await fetch('/fetch-data');

            if (!response.ok) {
                throw new Error(`HTTP error! status: ${response.status}`);
            }

            const result = await response.json();

            if (result.status !== 'success') {
                throw new Error(result.error || 'Unknown error occurred');
            }

            const data = result.data;

            const tableContainer = document.getElementById(`${tableId}-container`);
            tableContainer.innerHTML = ''; // Clear existing table data

            let tableHTML = `
                <table class="min-w-full bg-white text-sm">
                    <thead>
                        <tr class="bg-gray-200 text-gray-600 uppercase text-xs leading-normal">
                            <th class="py-3 px-4 text-left">No</th>
                            <th class="py-3 px-4 text-left">Merek</th>
                            <th class="py-3 px-4 text-left">Tipe</th>
                            ${tableId === 'data-table-penjualan' ? `
                                <th class="py-3 px-4 text-left">Bulan</th>
                                <th class="py-3 px-4 text-left">Jumlah Stok</th>
                                <th class="py-3 px-4 text-left">Jumlah Terjual</th>
                                <th class="py-3 px-4 text-left">Harga Satuan Rp</th>
                                <th class="py-3 px-4 text-left">Total Penjualan Rp</th>
                            ` : `
                                <th class="py-3 px-4 text-left">Kamera Utama MP</th>
                                <th class="py-3 px-4 text-left">Kamera Depan MP</th>
                                <th class="py-3 px-4 text-left">RAM</th>
                                <th class="py-3 px-4 text-left">Memori Internal</th>
                                <th class="py-3 px-4 text-left">Baterai mAh</th>
                                <th class="py-3 px-4 text-left">Jenis Layar</th>
                            `}
                        </tr>
                    </thead>
                    <tbody class="text-gray-600 text-xs font-light">
            `;

            data.forEach((item, index) => {
                tableHTML += `
                    <tr class="border-b border-gray-200 hover:bg-gray-100">
                        <td class="py-3 px-6 text-left">${index + 1}</td>
                        <td class="py-3 px-6 text-left">${item.Merek || '-'}</td>
                        <td class="py-3 px-6 text-left">${item.Tipe || '-'}</td>
                        ${tableId === 'data-table-penjualan' ? `
                            <td class="py-3 px-6 text-left">${item.Bulan || '-'}</td>
                            <td class="py-3 px-6 text-left">${item.Jumlah_Stok || '-'}</td>
                            <td class="py-3 px-6 text-left">${item.Jumlah_Terjual || '-'}</td>
                            <td class="py-3 px-6 text-left">${formatRupiah(item.Harga_Satuan_Rp) || '-'}</td>
                            <td class="py-3 px-6 text-left">${formatRupiah(item.Total_Penjualan_Rp) || '-'}</td>
                        ` : `
                            <td class="py-3 px-6 text-left">${item.Kamera_Utama_MP || '-'}</td>
                            <td class="py-3 px-6 text-left">${item.Kamera_Depan_MP || '-'}</td>
                            <td class="py-3 px-6 text-left">${item.RAM || '-'}</td>
                            <td class="py-3 px-6 text-left">${item.Memori_Internal || '-'}</td>
                            <td class="py-3 px-6 text-left">${item.Baterai_mAh || '-'}</td>
                            <td class="py-3 px-6 text-left">${item.Jenis_Layar || '-'}</td>
                        `}
                    </tr>
                `;
            });

            tableHTML += `
                    </tbody>
                </table>
            `;

            tableContainer.innerHTML = tableHTML;

            // Show the appropriate tab content
            document.querySelectorAll('#tab-content > div').forEach(div => div.classList.add('hidden'));
            document.getElementById(tabId).classList.remove('hidden');
        } catch (error) {
            console.error('Error fetching sales data:', error);
            // Optionally, display error message to user
            const errorMessage = document.getElementById('error-message');
            if (errorMessage) {
                errorMessage.textContent = `Failed to fetch data: ${error.message}`;
                errorMessage.style.display = 'block';
            }
        }
    }

    // Fetch visualizations
    async function fetchVisualizations() {
        try {
            let response = await fetch('/visualize', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify({
                    "threshold_start": 0.1,
                    "threshold_end": 0.5,
                    "num_iterations": 5
                }),
            });

            if (!response.ok) {
                throw new Error('Network response was not ok');
            }

            let data = await response.json();
            let images = data.images;
            let visualizationCards = document.getElementById('visualization-cards');

            visualizationCards.innerHTML = ''; // Clear existing visualization cards

            for (let key in images) {
                if (images.hasOwnProperty(key)) {
                    let imagePath = images[key];
                    let card = `
                        <div class="bg-white p-4 rounded-lg shadow">
                            <h3 class="text-lg font-bold mb-2">${key.replace(/_/g, ' ').replace(/(\b[a-z])/g, function(char) { return char.toUpperCase(); })}</h3>
                            <img src="${imagePath}" alt="${key}" class="w-full h-48 object-contain cursor-pointer" onclick="openModal('${key}', '${imagePath}')">
                        </div>
                    `;
                    visualizationCards.innerHTML += card;
                }
            }
        } catch (error) {
            console.error('Error fetching visualizations:', error);
        }
    }

    // Call functions when the document is ready
    fetchDataAndDisplay();
    fetchVisualizations();

    // Tab navigation
    document.querySelectorAll('ul > li > button').forEach(tab => {
        tab.addEventListener('click', function(e) {
            e.preventDefault();
            let tabContents = document.querySelectorAll('#tab-content > div');
            tabContents.forEach(content => content.classList.add('hidden'));
            let targetTab = this.getAttribute('onclick').match(/'([^']+)'/)[1];
            document.getElementById(targetTab.replace('fetchSalesData', 'tab')).classList.remove('hidden');

            document.querySelectorAll('ul > li > button').forEach(link => link.classList.remove('text-blue-700', 'font-semibold'));
            this.classList.add('text-blue-700', 'font-semibold');
        });
    });

    // Function to open input modal
    function openModalInput() {
        document.getElementById('modal-input').classList.remove('hidden');
    }

    // Function to close input modal
    function closeModalInput() {
        document.getElementById('modal-input').classList.add('hidden');
    }

    // Function to submit form
    function submitForm() {
        // Handle form submission logic here
        closeModalInput();
    }

    // Attach open and close modal handlers
    document.getElementById('open-modal-btn').addEventListener('click', openModalInput);
    document.getElementById('close-modal-btn').addEventListener('click', closeModalInput);
});
