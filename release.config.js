module.exports = {
    branches: [
        {
            name: "main",
            level: "minor"
        },
        {
            name: "zowe-v?-lts",
            level: "patch"
        }
        // {
        //     name: "next",
        //     prerelease: true
        // }
    ],
    plugins: [
        "@octorelease/changelog",
        "@octorelease/pypi",
        "@octorelease/github",
        "@octorelease/git"
    ]
};
