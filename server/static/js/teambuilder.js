
var pokeElements = new Array(6);
var pokeNames = new Array(6);

function setSlotToID(slot, id) {
    let div = document.getElementById(`div${slot}`);
    if(div.firstChild) {
        div.removeChild(div.firstChild);
    }
    pokeElements[slot] = id;

    if(id != -1) {
        // Set the slot pokemon ID, then set the image for that slot.
        let baseImg = document.getElementById(String(id));
        console.log(baseImg);
        pokeNames[slot] = baseImg.parentElement.textContent.toLowerCase();
        let img = baseImg.cloneNode(true);
        img.id = "-1"
        img.draggable = false;
        div.appendChild(img);
    } else {
        pokeNames[slot] = null;
    }
}

function saveAndEdit(id) {
    document.getElementById(`editButton${id}`).setAttribute(
        'value',
        JSON.stringify({
            edit: id,
            team: JSON.stringify(pokeElements),
            teamNames: JSON.stringify(pokeNames)
        })
    )
}

function save() {
    document.getElementById('submit').setAttribute(
        'value',
        JSON.stringify({
            team: JSON.stringify(pokeElements),
            teamNames: JSON.stringify(pokeNames)
        })
    )
}

function allowDrop(ev)
{
    ev.preventDefault();
    ev.dataTransfer.dropEffect= "copy";
}

function drag(ev)
{
    ev.dataTransfer.setData("image", ev.target.id);
    event.dropEffect = "copy";
}

function drop(ev, type)
{
    ev.preventDefault();
    var data = ev.dataTransfer.getData("image");
    let divID = parseInt(ev.target.id.slice(3));
    setSlotToID(divID, data);
}