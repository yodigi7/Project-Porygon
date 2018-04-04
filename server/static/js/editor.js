
function getNext(n)
{
    x = n.nextSibling;
    while(x.nodeType!=1)
    {
        x = x.nextSibling;
    }
    return x;
}

function showValue(self)
{
    getNext(self).innerHTML = self.value;
}