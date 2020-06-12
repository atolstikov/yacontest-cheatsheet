#include "testlib.h"

using namespace std;

int main(int argc, char * argv[])
{
    setName("scored checker");
    registerTestlibCmd(argc, argv);

    string token = ouf.readLine();

    if (token[0] == '$') {
        quitf(_wa, token.c_str());
    }

    double score = atof(token.c_str());

    quitp(max(0.0, score), "from file %.10lf", score);
}
