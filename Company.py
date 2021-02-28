class Company:

    def __init__(self, number, code, name, pdf, passed, der, pbv, roe, per):
        self.number = number
        self.code = code
        self.name = name
        self.pdf = pdf
        self.passed = passed

        self.der = der
        self.pbv = pbv
        self.roe = roe
        self.per = per

        self.latest_der = der[len(der)-1]
        self.latest_pbv = pbv[len(pbv)-1]
        self.latest_roe = roe[len(roe)-1]
        self.latest_per = per[len(per)-1]

    def to_string(self):
        return f"[{self.code}] {self.name}\n\tDER (X): {self.der[len(self.der)-1]}\n\tPBV (X): {self.pbv[len(self.pbv)-1]}\n\tROE (%): {self.roe[len(self.roe)-1]}\n\tPER (X): {self.per[len(self.per)-1]}\n\tInvest Here? {'YES' if self.passed else 'NO'}\n\n"
