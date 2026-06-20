import { useState, useEffect } from "react";
import { useParams, useNavigate } from "react-router-dom";
import paymentApi from "../api/paymentApi";

const PaymentPage = () => {
  const { payment_id } = useParams();
  const navigate = useNavigate();
  const [payment, setPayment] = useState(null);
  const [loading, setLoading] = useState(true);
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const [status, setStatus] = useState("CREATED"); // CREATED, PENDING, SUCCESS, FAILED

  useEffect(() => {
    fetchPaymentDetails();
  }, [payment_id]);

  const fetchPaymentDetails = async () => {
    try {
      const response = await paymentApi.get(`/payment/${payment_id}`);
      setPayment(response.data);
      setStatus(response.data.status);
    } catch (err) {
      setError("Failed to fetch payment details.");
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const handlePayment = async (manualStatus = null) => {
    setProcessing(true);
    setError("");
    try {
      const url = manualStatus ? `/pay/${payment_id}?status=${manualStatus}` : `/pay/${payment_id}`;
      const response = await paymentApi.post(url);
      setPayment(response.data);
      setStatus(response.data.status);
    } catch (err) {
      setError("Payment processing failed. Please try again.");
      console.error(err);
    } finally {
      setProcessing(false);
    }
  };

  if (loading) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <h2 style={titleStyle}>Loading Payment Details...</h2>
        </div>
      </div>
    );
  }

  if (error && !payment) {
    return (
      <div style={containerStyle}>
        <div style={cardStyle}>
          <h2 style={{ ...titleStyle, color: "#ff8a92" }}>Error</h2>
          <p style={{ color: "rgba(220, 232, 247, 0.8)" }}>{error}</p>
          <button onClick={() => navigate("/")} style={buttonStyle}>Back to Home</button>
        </div>
      </div>
    );
  }

  return (
    <div style={containerStyle}>
      <style>{`
        @keyframes spin {
          0% { transform: rotate(0deg); }
          100% { transform: rotate(360deg); }
        }
        @keyframes pulse {
          0% { transform: scale(1); opacity: 0.8; }
          50% { transform: scale(1.05); opacity: 1; }
          100% { transform: scale(1); opacity: 0.8; }
        }
      `}</style>

      <div style={cardStyle}>
        <div style={{ textAlign: "center", marginBottom: "2rem" }}>
          <div style={{ fontSize: "3rem", marginBottom: "1rem" }}>💳</div>
          <h2 style={titleStyle}>Secure Payment</h2>
          <p style={subtitleStyle}>Complete your booking payment for QuickHaul</p>
        </div>

        <div style={infoBoxStyle}>
          <div style={infoRowStyle}>
            <span>Payment ID</span>
            <span style={{ fontWeight: "600", color: "#5ef0ff" }}>{payment.payment_id}</span>
          </div>
          <div style={infoRowStyle}>
            <span>Booking ID</span>
            <span style={{ fontWeight: "600" }}>{payment.booking_id}</span>
          </div>
          <div style={dividerStyle} />
          <div style={infoRowStyle}>
            <span style={{ fontSize: "1.1rem" }}>Total Amount</span>
            <span style={{ fontSize: "1.5rem", fontWeight: "800", color: "#3d9fff" }}>₹{payment.amount.toLocaleString()}</span>
          </div>
        </div>

        <div style={{ marginTop: "2rem" }}>
          {status === "SUCCESS" ? (
            <div style={statusCardStyle("SUCCESS")}>
              <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>✅</div>
              <h3 style={{ margin: "0.5rem 0", color: "#1fffa8" }}>Payment Successful!</h3>
              <p style={{ color: "rgba(220, 232, 247, 0.7)", fontSize: "0.9rem" }}>Your booking has been confirmed. A notification has been sent.</p>
              <button onClick={() => navigate("/history")} style={{ ...buttonStyle, marginTop: "1.5rem" }}>View Booking History</button>
            </div>
          ) : status === "FAILED" ? (
            <div style={statusCardStyle("FAILED")}>
              <div style={{ fontSize: "2.5rem", marginBottom: "1rem" }}>❌</div>
              <h3 style={{ margin: "0.5rem 0", color: "#ff8a92" }}>Payment Failed</h3>
              <p style={{ color: "rgba(220, 232, 247, 0.7)", fontSize: "0.9rem" }}>There was an issue processing your payment. Please try again.</p>
              <button onClick={() => handlePayment()} style={{ ...buttonStyle, marginTop: "1.5rem" }}>Retry Payment</button>
            </div>
          ) : (
            <div style={{ display: "flex", flexDirection: "column", gap: "1rem" }}>
              <button
                disabled={processing}
                onClick={() => handlePayment()}
                style={{
                  ...buttonStyle,
                  background: processing ? "linear-gradient(135deg, #6b7280 0%, #9ca3af 100%)" : "linear-gradient(135deg, #3d9fff 0%, #5ef0ff 100%)",
                  animation: processing ? "pulse 2s infinite" : "none"
                }}
              >
                {processing ? "Processing..." : "Pay Now"}
              </button>

              <div style={{ display: "grid", gridTemplateColumns: "1fr 1fr", gap: "1rem" }}>
                <button
                  disabled={processing}
                  onClick={() => handlePayment("SUCCESS")}
                  style={{ ...buttonStyle, background: "rgba(31, 255, 168, 0.1)", border: "1px solid #1fffa8", color: "#1fffa8", fontSize: "0.85rem" }}
                >
                  Simulate Success
                </button>
                <button
                  disabled={processing}
                  onClick={() => handlePayment("FAILED")}
                  style={{ ...buttonStyle, background: "rgba(255, 95, 107, 0.1)", border: "1px solid #ff8a92", color: "#ff8a92", fontSize: "0.85rem" }}
                >
                  Simulate Failure
                </button>
              </div>
            </div>
          )}
        </div>

        {error && <div style={errorStyle}>{error}</div>}
      </div>
    </div>
  );
};

// Styles
const containerStyle = {
  minHeight: "100vh",
  background: "linear-gradient(135deg, #060d1a 0%, #0a1224 50%, #050c1a 100%)",
  display: "flex",
  alignItems: "center",
  justifyContent: "center",
  padding: "2rem",
  color: "#ffffff"
};

const cardStyle = {
  maxWidth: "500px",
  width: "100%",
  background: "linear-gradient(160deg, rgba(10, 18, 36, 0.95) 0%, rgba(6, 13, 26, 0.98) 100%)",
  border: "2px solid rgba(61, 159, 255, 0.3)",
  borderRadius: "22px",
  padding: "2.5rem",
  boxShadow: "0 24px 60px rgba(0, 0, 0, 0.8), 0 0 40px rgba(61, 159, 255, 0.2)",
};

const titleStyle = {
  fontSize: "1.8rem",
  fontWeight: "700",
  background: "linear-gradient(135deg, #ffffff 0%, #dce8f7 100%)",
  WebkitBackgroundClip: "text",
  WebkitTextFillColor: "transparent",
  marginBottom: "0.5rem"
};

const subtitleStyle = {
  color: "rgba(220, 232, 247, 0.7)",
  fontSize: "0.95rem"
};

const infoBoxStyle = {
  background: "rgba(255, 255, 255, 0.05)",
  borderRadius: "16px",
  padding: "1.5rem",
  border: "1px solid rgba(255, 255, 255, 0.1)",
  display: "flex",
  flexDirection: "column",
  gap: "0.75rem"
};

const infoRowStyle = {
  display: "flex",
  justifyContent: "space-between",
  alignItems: "center",
  fontSize: "0.9rem",
  color: "rgba(220, 232, 247, 0.9)"
};

const dividerStyle = {
  height: "1px",
  background: "rgba(255, 255, 255, 0.1)",
  margin: "0.5rem 0"
};

const buttonStyle = {
  width: "100%",
  padding: "1rem",
  fontSize: "1rem",
  fontWeight: "700",
  borderRadius: "12px",
  border: "none",
  cursor: "pointer",
  transition: "all 0.2s ease",
  color: "#04101f"
};

const errorStyle = {
  marginTop: "1rem",
  padding: "0.75rem",
  background: "rgba(255, 95, 107, 0.1)",
  border: "1px solid #ff8a92",
  borderRadius: "8px",
  color: "#ff8a92",
  fontSize: "0.85rem",
  textAlign: "center"
};

const statusCardStyle = (type) => ({
  padding: "2rem",
  borderRadius: "16px",
  background: type === "SUCCESS" ? "rgba(31, 255, 168, 0.05)" : "rgba(255, 95, 107, 0.05)",
  border: `1px solid ${type === "SUCCESS" ? "#1fffa8" : "#ff8a92"}`,
  textAlign: "center",
  display: "flex",
  flexDirection: "column",
  alignItems: "center"
});

export default PaymentPage;
