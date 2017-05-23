```python
def getUrls(filename):
    urls = []
    with open(filename) as fp:
        d = json.load(fp)
    for key in d:
        urls.append([key, d[key]]) 
    return urls
```

```swift
class currentUserInfo {
    static let sharedCurrentUserInstance = currentUserInfo()
    var userRealName = ""
    private init() {}
}