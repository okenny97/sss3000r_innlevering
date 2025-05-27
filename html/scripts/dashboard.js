document.addEventListener("DOMContentLoaded", () => {
    const addTestActivity = document.getElementById("add-test-activity");
    const logoutButton = document.getElementById("logout");
    const profileSettingsButton = document.getElementById("profile-settings");
    const activityFolders = document.getElementById("activity-folders");
    const liveViewBtn = document.getElementById("live-view-btn");

    let alarmOn = false;
    const activitiesPerDay = {};



    logoutButton.addEventListener("click", () => {
        window.location.href = "../html/login.html";
    });

    profileSettingsButton.addEventListener("click", () => {
        window.location.href = "../html/innstillinger.html";
    });

    function renderActivityFolders() {
        activityFolders.innerHTML = "";
        const dates = Object.keys(activitiesPerDay).sort().reverse();

        if (dates.length === 0) {
            activityFolders.innerHTML = "<p>Ingen aktiviteter ennå.</p>";
            return;
        }

        dates.forEach(dateKey => {
            const folder = document.createElement("button");
            folder.className = "list-group-item list-group-item-action";
            folder.textContent = dateKey;
            folder.addEventListener("click", () => openDayActivities(dateKey));
            activityFolders.appendChild(folder);
        });
    }

    function openDayActivities(dateKey) {
        const activities = activitiesPerDay[dateKey];
        const container = document.getElementById("day-activities-content");
        container.innerHTML = `<h5>Aktiviteter for ${dateKey}</h5><hr>`;

        if (!activities || activities.length === 0) {
            container.innerHTML += "<p>Ingen aktiviteter for denne dagen.</p>";
        } else {
            activities.forEach(activity => {
                const item = document.createElement("div");
                item.className = "mb-3";

                let content = `<p>${activity.time} - ${activity.description || ''}</p>`;

                if (activity.files && activity.folder) {
                    content += `<div class="d-flex flex-wrap">`;
                    activity.files.forEach(file => {
                        const filePath = `/media/pictures/${activity.folder}/${file}`;
                        const fileExtension = file.split('.').pop().toLowerCase();

                        if (["jpg", "jpeg", "png"].includes(fileExtension)) {
                            content += `
                                <img src="${filePath}" class="img-thumbnail m-1" style="width: 150px;" onclick='viewImage("${filePath}")'>`;
                        } else if (["mp4", "mov"].includes(fileExtension)) {
                            content += `
                                <video src="${filePath}" class="m-1" style="width: 150px;" controls></video>`;
                        }
                    });
                    content += `</div>`;
                }

                content += "<hr>";
                item.innerHTML = content;
                container.appendChild(item);
            });
        }
        const modal = new bootstrap.Modal(document.getElementById('dayActivitiesModal'));
        modal.show();
    }

    
    // Start eller stopp live kamera-feed
    
    liveViewBtn.addEventListener("click", () => {
        const liveCameraImage = document.getElementById("live-camera-feed");
        liveCameraImage.src = "/api/live-camera-feed"; 
    });
    
    // Når modalen lukkes, stopp kamera-feed for å spare CPU
    const liveViewModal = document.getElementById('liveViewModal');
    liveViewModal.addEventListener('hidden.bs.modal', () => {
        const liveCameraImage = document.getElementById('live-camera-feed');
        liveCameraImage.src = ""; 
    });


    });

function viewImage(imageSrc) {
    window.open(imageSrc, '_blank');
}

function viewVideo(videoSrc) {
    window.open(videoSrc, '_blank');
}