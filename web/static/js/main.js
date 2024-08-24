let selectedStore = null;

selectStore('tm_store')


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

        updateSummaryData(globalData)

        // Sort data by Year, then by Month
        globalData.sort((a, b) => (a.Tahun - b.Tahun) || (a.Bulan - b.Bulan));

        displayAccordionByYear();
    } catch (error) {
        console.error('Error fetching data:', error);
    }
}

function displayAccordionByYear() {
    const accordionContainer = document.getElementById('accordion-container');
    accordionContainer.innerHTML = ''; // Clear previous data

    const dataByYear = globalData.reduce((acc, item) => {
        if (!acc[item.Tahun]) {
            acc[item.Tahun] = {};
        }
        if (!acc[item.Tahun][item.Bulan]) {
            acc[item.Tahun][item.Bulan] = [];
        }
        acc[item.Tahun][item.Bulan].push(item);
        return acc;
    }, {});

    // Loop through years
    Object.keys(dataByYear).forEach(year => {
        let yearAccordion = document.createElement('div');
        yearAccordion.className = 'year-accordion border border-gray-300 rounded-lg my-2';

        // Create Year Header
        let yearHeader = document.createElement('div');
        yearHeader.className = 'year-header bg-gray-200 p-3 cursor-pointer';
        yearHeader.innerHTML = `<h2 class="text-lg font-bold">${year}</h2>`;
        yearHeader.addEventListener('click', () => toggleAccordion(yearAccordion));

        yearAccordion.appendChild(yearHeader);

        // Create Content for Each Year (accordion per month)
        let yearContent = document.createElement('div');
        yearContent.className = 'year-content hidden';

        Object.keys(dataByYear[year]).forEach(month => {
            let monthAccordion = document.createElement('div');
            monthAccordion.className = 'month-accordion my-2';

            let monthHeader = document.createElement('div');
            monthHeader.className = 'month-header bg-gray-100 p-2 cursor-pointer';
            monthHeader.innerHTML = `<h3 class="text-md font-medium">${getMonthName(month)}</h3>`;
            monthHeader.addEventListener('click', () => toggleAccordion(monthAccordion));

            let monthContent = document.createElement('div');
            monthContent.className = 'month-content hidden';

            let tableContainer = document.createElement('div');
            tableContainer.className = 'table-container';

            // Create the table for this month
            let table = createDataTable(dataByYear[year][month], month);

            // Append the table without pagination controls
            tableContainer.appendChild(table);

            monthContent.appendChild(tableContainer);
            monthAccordion.appendChild(monthHeader);
            monthAccordion.appendChild(monthContent);
            yearContent.appendChild(monthAccordion);
        });

        yearAccordion.appendChild(yearContent);
        accordionContainer.appendChild(yearAccordion);
    });
}

function createDataTable(data, month) {
    let table = document.createElement('table');
    table.className = 'w-full text-left table-auto';
    let tableHead = `
        <thead>
            <tr class="bg-gray-200">
                <th class="py-2 px-4">#</th>
                <th class="py-2 px-4">Cluster</th>
                <th class="py-2 px-4">Merek</th>
                <th class="py-2 px-4">Tipe</th>
                <th class="py-2 px-4">Kategori Penjualan</th>
                <th class="py-2 px-4">Persentase Terjual</th>
            </tr>
        </thead>`;
    table.innerHTML = tableHead;

    let tableBody = document.createElement('tbody');
    tableBody.id = `data-table-${month}`;

    // Add all rows without pagination
    data.forEach((item, index) => {
        let row = `
            <tr class="border-b border-gray-200 hover:bg-gray-100">
                <td class="py-2 px-4">${index + 1}</td>
                <td class="py-2 px-4">${item.Cluster}</td>
                <td class="py-2 px-4">${item.Merek}</td>
                <td class="py-2 px-4">${item.Tipe}</td>
                <td class="py-2 px-4">${item.Kategori_Penjualan}</td>
                <td class="py-2 px-4">${item.Persentase_Jumlah_Terjual.toFixed(4)}%</td>
            </tr>
        `;
        tableBody.innerHTML += row;
    });

    table.appendChild(tableBody);
    return table;
}

function toggleAccordion(accordion) {
    const content = accordion.querySelector('.year-content') || accordion.querySelector('.month-content');
    if (content) {
        content.classList.toggle('hidden');
    }
}

function getMonthName(month) {
    const monthNames = {
        "Jan": "January",
        "Feb": "February",
        "Mar": "March",
        "Apr": "April",
        "May": "May",
        "Jun": "June",
        "Jul": "July",
        "Aug": "August",
        "Sep": "September",
        "Oct": "October",
        "Nov": "November",
        "Dec": "December"
    };
    return monthNames[month];
}


function updateSummaryData(data) {
    // Menghitung data unik untuk Card 1
    let uniqueMerek = new Set();
    let uniqueTipe = new Set();
    let uniqueBulan = new Set();
    let uniqueTahun = new Set();
    let uniqueCluster = new Set();

    data.forEach(item => {
        uniqueMerek.add(item.Merek);
        uniqueTipe.add(item.Tipe);
        uniqueBulan.add(item.Bulan);
        uniqueTahun.add(item.Tahun);
        uniqueCluster.add(item.Cluster);
    });

    // Count categories for Card 2
    let categoryCounts = {
        'Sangat Rendah': 0,
        'Rendah': 0,
        'Cukup': 0,
        'Tinggi': 0,
        'Sangat Tinggi': 0
    };

    let totalCategoryCount = 0;  // Initialize total count

    data.forEach(item => {
        categoryCounts[item.Kategori_Penjualan]++;
        totalCategoryCount++;  // Increment total count
    });

    document.getElementById('unique-merek').textContent = uniqueMerek.size;
    document.getElementById('unique-tipe').textContent = uniqueTipe.size;
    document.getElementById('unique-bulan').textContent = uniqueBulan.size;
    document.getElementById('unique-cluster').textContent = uniqueCluster.size;
    // Display the total sum of categories in the div with id "sum-total-category"
    document.getElementById('sum-total-category').textContent = totalCategoryCount;

    // Menghitung jumlah kategori penjualan per tahun
    let yearCategoryCounts = {};
    let yearTotals = {}; // Menyimpan total untuk setiap tahun

    data.forEach(item => {
        let year = item.Tahun;
        let category = item.Kategori_Penjualan;

        if (!yearCategoryCounts[year]) {
            yearCategoryCounts[year] = {
                'Sangat Rendah': 0,
                'Rendah': 0,
                'Cukup': 0,
                'Tinggi': 0,
                'Sangat Tinggi': 0
            };
            yearTotals[year] = 0; // Inisialisasi total per tahun
        }

        yearCategoryCounts[year][category]++;
        yearTotals[year]++; // Menambah total untuk tahun yang sesuai
    });

    // Mengambil elemen tabel
    let categoryTableBody = document.getElementById('category-summary-table-body');
    let categoryTableHeader = document.getElementById('category-summary-table-header');
    let categoryTableFooter = document.getElementById('category-summary-table-footer'); // Elemen footer tabel

    // Kosongkan tabel sebelum mengisi data baru
    categoryTableBody.innerHTML = ''; 
    categoryTableHeader.innerHTML = ''; 
    categoryTableFooter.innerHTML = ''; 

    // Ambil semua tahun dan kategori
    let years = Object.keys(yearCategoryCounts).sort();
    let categories = ['Sangat Rendah', 'Rendah', 'Cukup', 'Tinggi', 'Sangat Tinggi'];

    // Buat header tabel
    let headerRow = `<th class="py-3 px-6 text-left font-medium text-gray-600 uppercase tracking-wider">Kategori Penjualan</th>`;
    years.forEach(year => {
        headerRow += `<th class="py-3 px-6 text-center font-medium text-gray-600 uppercase tracking-wider">${year}</th>`;
    });
    categoryTableHeader.innerHTML = `<tr>${headerRow}</tr>`;

    // Buat isi tabel berdasarkan kategori
    categories.forEach(category => {
        let row = `<tr class="border-b border-gray-200 hover:bg-gray-100">
                    <td class="py-3 px-6 text-left font-medium text-gray-600">${category}</td>`;
        years.forEach(year => {
            let count = yearCategoryCounts[year][category] || 0; // Jika tidak ada data, tampilkan 0
            row += `<td class="py-3 px-6 text-center">${count}</td>`;
        });
        row += '</tr>';
        categoryTableBody.innerHTML += row;
    });

    // Buat footer tabel untuk menampilkan total per tahun
    let footerRow = `<th class="py-3 px-6 text-left font-medium text-gray-600 uppercase tracking-wider">Total per Tahun</th>`;
    years.forEach(year => {
        footerRow += `<th class="py-3 px-6 text-center font-medium text-gray-600 uppercase tracking-wider">${yearTotals[year]}</th>`;
    });
    categoryTableFooter.innerHTML = `<tr>${footerRow}</tr>`;
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
    fetchSalesData('tab-penjualan', 'data-table-penjualan', storeName)
    
    
}


function selectStore(storeName) {
    
    selectedStore = storeName;
     // Menggunakan textContent untuk memperbarui teks
    showData(selectedStore);
    
}


async function fetchSalesData(tabId, tableId, namaToko) {
    
    if (!namaToko) {
        console.error('Nama toko belum dipilih.');
        return;
    }

    try {
       
        console.log(namaToko)
        // Mengirim request ke endpoint dengan parameter nama toko
        const response = await fetch(`/fetch-data/${namaToko}`);

        if (!response.ok) {
            throw new Error(`HTTP error! status: ${response.status}`);
        }

        const result = await response.json();

        // Periksa apakah data memiliki struktur yang diharapkan
        if (!result.data) {
            throw new Error(result.error || 'Unknown error occurred');
        }

        let data = Object.values(result.data); // Convert data object to array

        // Filter data untuk menghilangkan duplikasi berdasarkan Merek dan Tipe (hanya untuk tabel spesifikasi)
        if (tableId === 'data-table-spesifikasi') {
            const uniqueData = {};
            data = data.filter(item => {
                const key = `${item.Merek}-${item.Tipe}`;
                if (!uniqueData[key]) {
                    uniqueData[key] = true;
                    return true;
                }
                return false;
            });
        }

        // Urutkan data berdasarkan tahun dan bulan DESC
        data = data.sort((a, b) => {
            const [monthA, yearA] = a.Bulan.split(' ');
            const [monthB, yearB] = b.Bulan.split(' ');
            const monthOrder = ["Jan", "Feb", "Mar", "Apr", "May", "Jun", "Jul", "Aug", "Sep", "Oct", "Nov", "Dec"];

            // Urutkan berdasarkan tahun DESC, lalu bulan DESC
            if (yearA !== yearB) {
                return parseInt(yearB) - parseInt(yearA);
            } else {
                return monthOrder.indexOf(monthB) - monthOrder.indexOf(monthA);
            }
        });

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
                            <th class="py-3 px-4 text-left">Tahun</th>
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

        // Iterasi melalui data yang sudah diurutkan
        data.forEach((item, index) => {
            tableHTML += `
                <tr class="border-b border-gray-200 hover:bg-gray-100">
                    <td class="py-3 px-6 text-left">${index + 1}</td>
                    <td class="py-3 px-6 text-left">${item.Merek || '-'}</td>
                    <td class="py-3 px-6 text-left">${item.Tipe || '-'}</td>
                    ${tableId === 'data-table-penjualan' ? `
                        <td class="py-3 px-6 text-left">${item.Bulan || '-'}</td>
                        <td class="py-3 px-6 text-left">${item.Tahun || '-'}</td>
                        <td class="py-3 px-6 text-left">${item.Jumlah_Stok || '-'}</td>
                        <td class="py-3 px-6 text-left">${item.Jumlah_Terjual || '-'}</td>
                        <td class="py-3 px-6 text-left">${item.Harga_Satuan_Rp || '-'}</td>
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

function formatRupiah(value) {
    // Replace null with 0
    if (value === null) {
        value = 0;
    }

    // Convert the value to a locale string in Indonesian Rupiah format
    return value.toLocaleString('id-ID', {
        style: 'currency',
        currency: 'IDR'
    });
}

function hitungTotalPenjualan() {
    const hargaSatuan = document.getElementById('harga-satuan').value || 0;
    const unitTerjual = document.getElementById('unit-terjual').value || 0;
    const totalPenjualan = hargaSatuan * unitTerjual;
    document.getElementById('total-penjualan').value = formatRupiah(totalPenjualan);
}