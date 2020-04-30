function tallyMarks(count) {
    function generateTallyMark(number) {
        const outerSpan = document.createElement("span");
        outerSpan.style.display = "inline-block";

        for (let i = 0; i < number; i++)
        {
            const span = document.createElement("span");
            span.style.display = "inline-block";
            if (i == 4) {
                span.innerHTML = "/"
                span.style.transform = `scaleX(2.5) translateX(${ -15 - Math.random() * 3 }px) translateY(${ Math.random() * 3 }px) rotate(${ Math.random() * 20 }deg)`;
            }
            else {
                span.innerHTML = "l"
                span.style.transform = `skewX(${ -Math.random() * 20 }deg) translateX(${ Math.random() * 3 }px) translateY(${ Math.random() * 3 }px)`;
            }

            outerSpan.appendChild(span);
        }
        return outerSpan;
    };

    const result = [];
    for (let i = 0; i < (count / 5) - 1; i++) {
        result.push(generateTallyMark(5));
        result.push(document.createTextNode(" "));
    }

    const remainder = count % 5;
    if (remainder != 0)
    {
        result.push(generateTallyMark(remainder));
    }

    return result;
};

function countryDropdownItems() {
    return Object.keys(countryData)
        .sort()
        .map(countryCode => {
            const anchor = document.createElement("a");
            anchor.className = "dropdown-item text-muted country-dropdown-item";
            anchor.innerText = countryData[countryCode]["name"];
            anchor.addEventListener('click', () => {
                displayCountry(countryCode);
            });
            return anchor;
        });
}

function displayCountry(countryCode, updateURL = true) {
    if (!(countryCode in countryData)) {
        countryCode = "US";
    }

    const dropdownButton = document.querySelector("#country-dropdown-menu-button");
    dropdownButton.innerText = countryData[countryCode]["name"];

    const startDate = new Date(countryData[countryCode]["start"]);
    const endDate = new Date();
    let stillOnLockdown = true;
    if ("end" in countryData[countryCode]) {
        endDate = new Date(countryData[countryCode]["end"]);
        stillOnLockdown = false;
    }

    const durationDays = Math.ceil((endDate - startDate) / (1000 * 60 * 60 * 24));

    const lockdownText = document.querySelector("#lockdown-text");
    if (stillOnLockdown) {
        lockdownText.innerText = ` on lockdown since ${ startDate.toLocaleDateString() }`;
    }
    else {
        lockdownText.innerText = ` was on lockdown from ${ startDate.toLocaleDateString() } till ${ endDate.toLocaleDateString() }`;
    }

    const tallyContainer = document.querySelector("#tally");
    tallyContainer.innerHTML = "";
    tallyMarks(durationDays).forEach(element => tallyContainer.appendChild(element));

    document.querySelector("#total").innerHTML = durationDays + " day" + (durationDays > 1 ? "s" : "");

    if (updateURL) {
        history.replaceState(null, null, `?${ countryCode }`);
    }
}

function detectAndDisplayCountry() {
    fetch("http://ip-api.com/json/?fields=countryCode")
    .then((response) => response.json())
    .then((result) => {
        if ("countryCode" in result) {
            displayCountry(result["countryCode"], false);
        }
        else {
            displayCountry("");
        }
    })
    .catch((error) => {
        displayCountry("");
    });
}

document.addEventListener("DOMContentLoaded", event => {
    const dropdownItems = document.querySelector("[aria-labelledby=\"country-dropdown-menu-button\"]");
    dropdownItems.innerHTML = "";
    countryDropdownItems().forEach(element => dropdownItems.appendChild(element));

    let countryCode = "";
    if (document.location.search.length == 3 && document.location.search[0] === "?") {
        countryCode = document.location.search.slice(1, 3);
    }

    if (countryCode in countryData) {
        displayCountry(countryCode);
    }
    else {
        detectAndDisplayCountry();
    }
});
