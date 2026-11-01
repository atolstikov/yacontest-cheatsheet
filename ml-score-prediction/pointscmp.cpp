#include "testlib.h"

#include <cstdlib>
#include <string>

using namespace std;

int main(int argc, char *argv[])
{
    setName("scored checker");
    registerTestlibCmd(argc, argv);

    string token = ouf.readLine();
    if (token.empty()) {
        quitf(_pe, "empty output");
    }

    char *end = 0;
    double score = strtod(token.c_str(), &end);
    if (end == token.c_str()) {
        quitf(_wa, "%s", token.c_str());
    }
    while (*end == ' ' || *end == '\t') {
        ++end;
    }
    if (*end != '\0') {
        quitf(_wa, "%s", token.c_str());
    }
    if (score < 0) {
        score = 0;
    }
    quitp(score, "score %.10f", score);
}
