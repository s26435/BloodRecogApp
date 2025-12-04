//odpowaiada za dodawanie zdjecia oraz widzenie go w podgladzie obok co dodajemy 
// which is preety cool if u ask me
console.log("dziala")
document.addEventListener("DOMContentLoaded",() => {
    const form = document.querySelector(".upload-form");
    const clearBtn = document.querySelector(".btn-ghost");
    const previewContainer = document.querySelector(".upload-preview-placeholder");
    const fileInput = document.getElementById("analysis-image");

    if (form) {
        form.addEventListener("submit", async (Event) => { //event przekreslao jak cos
            Event.preventDefault();
            const formData = new FormData(form);

            try {
                const response = await fetch("/api/analyses", {
                    method: "POST",
                    body: formData,
                });
                if (!response.ok) {
                    let err={};
                    try {
                        err = await response.json();
                    } catch (e) {}
                    alert(err.detail || "Uruchomienie się nie powiodło :(");
                    return;
                }

                const data = await response.json();
                const analysisId = data.analysis.id;
                window.location.href = `/history?analysis_id=${encodeURIComponent(analysisId)}`;
            } catch (error) {
                console.error(error);
                alert("Bład połączenia z serwerem :(");
            }
        });
    }

    if (clearBtn&&form) { //odpowiada za wyczysczenie formularza
        clearBtn.addEventListener("click",() => {
            form.reset();
            if (previewContainer) {
                previewContainer.innerHTML ='<span class="upload-preview-label">Podgląd pojawi się tutaj</span>';
            }
        });
    }

    if (fileInput && previewContainer) { //odpowiada za pokazywanie preview
        fileInput.addEventListener("change", () => {
            const file = fileInput.files && fileInput.files[0];
            if (!file) return;

            const reader = new FileReader();
            reader.onload = (e) => {
                previewContainer.innerHTML = "";
                const img = document.createElement("img");
                img.src = e.target.result;
                img.alt = "Podgląd obrazu";
                img.className = "upload-preview-image";
                previewContainer.appendChild(img);
            };
            reader.readAsDataURL(file);
        });
    }
});



