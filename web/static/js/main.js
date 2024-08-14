
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
                    body: JSON.stringify({
                        dataSpec,
                        dataPenjualan
                    })
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

    // Fetch data and display in table
    let currentPage = 1;
    const rowsPerPage = 100;
    let totalPages = 1;
    let globalData = [];
    async function fetchDataAndDisplay(storeName) {
    try {
        // Construct the URL for the POST request
        const url = `/perform-clustering`;

        let response = await fetch(url, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify({
                "store": storeName,
                "threshold": 0.3
            }),
        });

        if (!response.ok) {
            throw new Error('Network response was not ok');
        }

        let data = await response.json();
        globalData = data.data;

        // Sort data by Cluster
        globalData.sort((a, b) => a.Cluster - b.Cluster);

        totalPages = Math.ceil(globalData.length / rowsPerPage);
        displayPage(1);
        setupPagination();
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function displayPage(page) {
    currentPage = page;
    let tableBody = document.getElementById('data-table-cluster');
    tableBody.innerHTML = ''; // Clear existing table data

    const startIndex = (page - 1) * rowsPerPage;
    const endIndex = Math.min(startIndex + rowsPerPage, globalData.length);

    for (let i = startIndex; i < endIndex; i++) {
        let item = globalData[i];
        let row = `
            <tr class="border-b border-gray-200 hover:bg-gray-100">
                <td class="py-3 px-6 text-left">${i + 1}</td>
                <td class="py-3 px-6 text-left">${item.Cluster}</td>
                <td class="py-3 px-6 text-left">${item.Kategori_Penjualan}</td>
                <td class="py-3 px-6 text-left">${item.Bulan}</td>
                <td class="py-3 px-6 text-left">${item.Merek}</td>
                <td class="py-3 px-6 text-left">${item.Persentase_Jumlah_Terjual.toFixed(4)}%</td>
                <td class="py-3 px-6 text-left">${item.Tipe}</td>
            </tr>
        `;
        tableBody.innerHTML += row;
    }

    // Update summary data only once (not per page)
    if (page === 1) {
        updateSummaryData(globalData);
    }
}

function setupPagination() {
    let pagination = document.getElementById('pagination');
    pagination.innerHTML = ''; // Clear existing pagination

    for (let i = 1; i <= totalPages; i++) {
        let pageLink = document.createElement('a');
        pageLink.href = '#';
        pageLink.textContent = i;
        pageLink.className = `pagination-link py-2 px-4 border border-gray-300 rounded-md text-gray-700 hover:bg-gray-100 hover:text-gray-900 transition-colors duration-300 text-sm font-medium`;

        if (i === currentPage) {
            pageLink.className += ' bg-blue-500 text-white border-blue-500';
        }

        pageLink.addEventListener('click', (e) => {
            e.preventDefault();
            displayPage(i);
        });

        pagination.appendChild(pageLink);
    }
}

function updateSummaryData(data) {
    // Count unique values for Card 1
    let uniqueMerek = new Set();
    let uniqueTipe = new Set();
    let uniqueBulan = new Set();
    let uniqueCluster = new Set();

    data.forEach(item => {
        uniqueMerek.add(item.Merek);
        uniqueTipe.add(item.Tipe);
        uniqueBulan.add(item.Bulan);
        uniqueCluster.add(item.Cluster);
    });

    document.getElementById('unique-merek').textContent = uniqueMerek.size;
    document.getElementById('unique-tipe').textContent = uniqueTipe.size;
    document.getElementById('unique-bulan').textContent = (uniqueBulan.size) - 1;
    document.getElementById('unique-cluster').textContent = uniqueCluster.size;

    // Count categories for Card 2
    let categoryCounts = {
        'Sangat Rendah': 0,
        'Rendah': 0,
        'Cukup': 0,
        'Tinggi': 0,
        'Sangat Tinggi': 0
    };

    data.forEach(item => {
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
}


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



function openModalInput() {
    document.getElementById('input-modal').classList.remove('hidden');
    document.getElementById('form-container').classList.remove('hidden');
    document.getElementById('data-penjualan-form').classList.remove('hidden');
    document.getElementById('data-spesifikasi-form').classList.remove('hidden');
}

function closeInputModal() {
    document.getElementById('input-modal').classList.add('hidden');
    document.getElementById('form-container').classList.add('hidden');
}

function openModal(title, imagePath) {
    const modalTitle = document.getElementById('modal-title');
    const modalImage = document.getElementById('modal-image');
    const imageModal = document.getElementById('image-modal');
    // Set the title and image source
    modalTitle.textContent = title.replace(/_/g, ' ').replace(/(\b[a-z])/g, function(char) {
        return char.toUpperCase();
    });
    modalImage.src = imagePath;
    // Show the modal
    imageModal.classList.remove('hidden');
}
// Function to close the modal
function closeModal() {
    document.getElementById('image-modal').classList.add('hidden');
}

   
showData('tm_store');
function showData(storeName) {
    fetchDataAndDisplay(storeName);
}
